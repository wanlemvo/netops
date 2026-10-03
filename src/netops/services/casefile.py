from __future__ import annotations

import base64
import binascii
import re
from html import escape
from io import BytesIO
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from markdown_it import MarkdownIt
from PIL import Image, ImageOps, UnidentifiedImageError

from netops.domain.models import new_id
from netops.domain.validation import NotFoundError, UserInputError, normalize_required_text


def render_text(value, format='markdown'):
    if format == 'plain':
        return '<p>' + escape(value or '').replace('\n', '<br>') + '</p>'
    parser = MarkdownIt('commonmark', {'html': False, 'breaks': True}).enable('table').disable('image')
    return parser.render(value or '')


def source_sections(person_id, source):
    """Read-only section projection. No imported bytes/dates become structured events."""
    if not source:
        return []
    lines = source.splitlines(keepends=True)
    parser = MarkdownIt('commonmark', {'html': False})
    headings = [(t.map[0], t.map[1], tokens[i + 1].content)
                for tokens in [parser.parse(source)] for i, t in enumerate(tokens)
                if t.type == 'heading_open' and t.map]
    boundaries = sorted(set([0, len(lines)] + [h[0] for h in headings]))
    titles = {start: (end, title) for start, end, title in headings}
    result = []
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:])):
        heading_end, title = titles.get(start, (start, 'Background / source material'))
        body = ''.join(lines[heading_end:end]).strip()
        if not body and not title:
            continue
        result.append({'section_id': uuid5(NAMESPACE_URL, f'netops:dossier:{person_id}:{index}').hex,
            'person_id': person_id, 'title': title, 'body': body, 'format': 'markdown', 'revision': 0,
            'created_at': None, 'updated_at': None, 'source_material': True})
    return result


class CasefileService:
    def __init__(self, repository, people):
        self.repository, self.people = repository, people

    def sections(self, person_id):
        person = self.people.get_v1_person(person_id)
        originals = source_sections(person.person_id, person.dossier)
        saved = {s['section_id']: s for s in self.repository.list_dossier_sections(person.person_id)}
        result = [saved.pop(s['section_id'], s) for s in originals] + list(saved.values())
        for item in result:
            item['html'] = render_text(item['body'], item['format'])
            # Original source is preserved; corrections use ordinary prose controls.
        return result

    def save_section(self, person_id, payload, section_id=None):
        person = self.people.get_v1_person(person_id)
        existing = None
        if section_id:
            existing = next((s for s in self.sections(person.person_id) if s['section_id'] == section_id), None)
            if existing is None:
                raise NotFoundError('Dossier section was not found.')
        title = normalize_required_text(payload.get('title'), 'Section title')
        body = normalize_required_text(payload.get('body'), 'Section text')
        format = 'plain'
        if payload.get('append') and existing:
            format = existing['format']
            if format == 'markdown':
                body = re.sub(r'([\\`*_{}\[\]()#+.!<>|~-])', r'\\\1', body)
            body = existing['body'] + '\n\n' + body
        return self.repository.save_dossier_section(person.person_id, section_id or new_id(), title, body,
            original=existing, expected_revision=payload.get('revision'), format=format)

    def set_photo(self, person_id, payload):
        person = self.people.get_v1_person(person_id)
        if payload.get('remove'):
            return self.people.update_v1_person_field(person.person_id, 'profile_photo_path', None).model_dump(mode='json')
        try:
            raw = base64.b64decode(payload.get('data', ''), validate=True)
            if not raw or len(raw) > 8 * 1024 * 1024:
                raise UserInputError('Choose a still image smaller than 8 MB.')
            with Image.open(BytesIO(raw)) as photo:
                if photo.format not in {'PNG', 'JPEG', 'WEBP'} or getattr(photo, 'n_frames', 1) != 1:
                    raise UserInputError('Choose a still PNG, JPEG or WebP photo.')
                if photo.width * photo.height > 24_000_000:
                    raise UserInputError('Choose a photo smaller than 24 megapixels.')
                photo.load()
                normalized = ImageOps.exif_transpose(photo).convert('RGB')
                normalized.thumbnail((1600, 1600))
                output = BytesIO()
                normalized.save(output, format='JPEG', quality=90)
        except (ValueError, binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
            raise UserInputError('The selected file is not a valid supported photo.') from exc
        db_file = self.repository.connection.execute('PRAGMA database_list').fetchone()[2]
        if not db_file:
            raise UserInputError('Photos require a saved workspace.')
        relative = Path('assets/profile_photos') / f'{person.person_id}-{new_id()}.jpg'
        destination = Path(db_file).parent / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            destination.write_bytes(output.getvalue())
            return self.people.update_v1_person_field(person.person_id, 'profile_photo_path', relative.as_posix()).model_dump(mode='json')
        except Exception:
            destination.unlink(missing_ok=True)  # Only this newly created, uniquely named photo.
            raise
