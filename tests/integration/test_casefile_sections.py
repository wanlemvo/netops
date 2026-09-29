import base64
from io import BytesIO
import shutil

from PIL import Image
import pytest

from netops.services.app_backend import NetworkOpsBackend
from netops.storage import NetOpsRepository, connect
from netops.domain.validation import UserInputError


def test_sections_preserve_source_render_safely_and_keep_revisions(tmp_path):
    backend = NetworkOpsBackend(NetOpsRepository(connect(tmp_path / 'test.sqlite3')))
    source = '# Background\n**Known** context\n\n## Preferences\n- Written agendas\n<script>alert(1)</script>'
    person = backend.create_person({'name': 'Fictional Person', 'dossier': source})['person_id']
    sections = backend.casefile.sections(person)
    assert len(sections) == 2
    assert '<strong>Known</strong>' in sections[0]['html']
    assert '<script>' not in sections[1]['html']
    original = sections[0]
    saved = backend.casefile.save_section(person, {'title': original['title'], 'body': '*Literal addition*', 'append': True, 'revision': 0}, original['section_id'])
    rendered = backend.casefile.sections(person)[0]['html']
    assert '<strong>Known</strong>' in rendered
    assert '*Literal addition*' in rendered
    assert backend.get_person(person)['dossier'] == source
    with pytest.raises(UserInputError, match='changed'):
        backend.casefile.save_section(person, {'title': 'Stale', 'body': 'Stale text', 'revision': 0}, original['section_id'])
    backend.casefile.save_section(person, {'title': 'Background', 'body': 'Corrected\nSecond line', 'revision': saved['revision']}, original['section_id'])
    history = backend.repository.dossier_section_history(person, original['section_id'])
    assert len(history) == 2 and history[-1]['body'] == original['body']
    backend.repository.connection.close()


def test_photos_remain_portable_and_reject_non_images(tmp_path):
    home = tmp_path / 'original workspace'; home.mkdir()
    backend = NetworkOpsBackend(NetOpsRepository(connect(home / 'test.sqlite3')))
    person = backend.create_person({'name': 'Fictional Portrait'})['person_id']
    image = BytesIO(); Image.new('RGB', (20, 30), 'blue').save(image, 'PNG')
    updated = backend.casefile.set_photo(person, {'data': base64.b64encode(image.getvalue()).decode()})
    relative = updated['profile_photo_path']
    assert relative.startswith('assets/profile_photos/')
    assert (home / relative).is_file()
    with pytest.raises(UserInputError):
        backend.casefile.set_photo(person, {'data': base64.b64encode(b'not a photo').decode()})
    backend.repository.connection.close()
    moved = tmp_path / 'renamed portable workspace'; shutil.copytree(home, moved)
    restored = NetworkOpsBackend(NetOpsRepository(connect(moved / 'test.sqlite3')))
    assert (moved / restored.get_person(person)['profile_photo_path']).is_file()
    restored.casefile.set_photo(person, {'remove': True})
    assert restored.get_person(person)['profile_photo_path'] is None
    assert (moved / relative).is_file()  # Retain prior assets for backup/history.
    restored.repository.connection.close()
