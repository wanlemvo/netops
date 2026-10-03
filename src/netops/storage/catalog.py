"""Persistent vocabularies and a single application representation for tags."""
import json

from netops.domain.models import new_id, now_iso
from netops.domain.validation import UserInputError, normalize_required_text

DEFAULT_TYPES = {
    'interaction': ['Meeting', 'Call', 'Text / Message', 'Email', 'Introduction', 'Event', 'Chance Encounter', 'Note', 'Other'],
    'relationship': ['Friend', 'Coworker', 'Former Coworker', 'Manager', 'Former Manager', 'Mentor', 'Mentee', 'Classmate', 'Professor', 'Recruiter', 'Professional Contact', 'Acquaintance', 'Family', 'Introduced By', 'Works With', 'Knows', 'Other'],
}


def normalized(value):
    return ' '.join(str(value).split()).casefold()


def ensure_type(connection, kind, label):
    if kind not in DEFAULT_TYPES:
        raise UserInputError('Unknown vocabulary.')
    label = ' '.join(normalize_required_text(label, 'Type').split())
    connection.execute('INSERT OR IGNORE INTO vocabulary VALUES (?, ?, ?, ?, ?)', (new_id(), kind, label, normalized(label), now_iso()))
    return dict(connection.execute('SELECT * FROM vocabulary WHERE kind=? AND normalized_name=?', (kind, normalized(label))).fetchone())


def tag_groups(connection):
    groups = {}
    for row in connection.execute('SELECT * FROM tags ORDER BY created_at, tag_id'):
        groups.setdefault(normalized(row['name']), []).append(dict(row))
    return groups


def ensure_tag(connection, label):
    label = ' '.join(normalize_required_text(label, 'Tag').split())
    group = tag_groups(connection).get(normalized(label))
    if group:
        row = group[0]
        connection.execute('UPDATE tags SET archived_at=NULL WHERE tag_id=?', (row['tag_id'],))
        return row
    stamp = now_iso()
    row = dict(tag_id=new_id(), name=label, normalized_name=normalized(label), created_at=stamp, updated_at=stamp, archived_at=None)
    connection.execute('INSERT INTO tags VALUES (:tag_id,:name,:normalized_name,:created_at,:updated_at,:archived_at)', row)
    return row


def backfill_catalog(connection):
    for kind, values in DEFAULT_TYPES.items():
        for value in values:
            ensure_type(connection, kind, value)
    for kind, table in [('interaction', 'interactions'), ('relationship', 'relationship_links')]:
        for row in connection.execute(f'SELECT DISTINCT {kind}_type AS label FROM {table}'):
            if row['label'] and row['label'].strip():
                ensure_type(connection, kind, row['label'])
    # Retain original JSON and historical tag/tagging IDs. Equivalent legacy labels
    # are grouped in the application; no personal records are deleted to deduplicate.
    for row in connection.execute('SELECT id, tags FROM people'):
        try:
            labels = json.loads(row['tags'] or '[]')
        except (TypeError, ValueError):
            continue
        if not isinstance(labels, list):
            continue
        for label in labels:
            if not str(label).strip():
                continue
            tag = ensure_tag(connection, str(label))
            connection.execute('INSERT OR IGNORE INTO taggings VALUES (?, ?, ?, ?, ?)', (new_id(), tag['tag_id'], 'person', row['id'], now_iso()))


class CatalogRepository:
    def catalog(self):
        return {kind: [dict(r) for r in self.connection.execute('SELECT * FROM vocabulary WHERE kind=? ORDER BY label COLLATE NOCASE', (kind,))] for kind in DEFAULT_TYPES} | {'tags': self.list_catalog_tags()}

    def save_type(self, kind, label):
        with self.connection:
            return ensure_type(self.connection, kind, label)

    def save_catalog_tag(self, label):
        with self.connection:
            return ensure_tag(self.connection, label)

    def list_catalog_tags(self):
        cache_key = (self.connection.total_changes, self.connection.execute('PRAGMA data_version').fetchone()[0])
        cached = getattr(self, '_tag_catalog_cache', None)
        if cached and cached[0] == cache_key:
            return cached[1]
        result = []
        for group in tag_groups(self.connection).values():
            if all(row['archived_at'] for row in group):
                continue
            ids = [row['tag_id'] for row in group]
            people = [r[0] for r in self.connection.execute(f"SELECT DISTINCT g.entity_id FROM taggings g JOIN people p ON p.id=g.entity_id WHERE g.entity_type='person' AND p.archived_at IS NULL AND g.tag_id IN ({','.join('?' for _ in ids)})", ids)]
            result.append({**group[0], 'people': people, 'usage': len(people)})
        result = sorted(result, key=lambda r: normalized(r['name']))
        self._tag_catalog_cache = (cache_key, result)
        return result

    def person_tag_names(self, person_id):
        return [tag['name'] for tag in self.list_catalog_tags() if person_id in tag['people']]

    def set_person_tags(self, person_id, labels):
        with self.connection:
            rows = [ensure_tag(self.connection, label) for label in labels]
            self.connection.execute("DELETE FROM taggings WHERE entity_type='person' AND entity_id=?", (person_id,))
            for row in rows:
                self.connection.execute('INSERT OR IGNORE INTO taggings VALUES (?, ?, ?, ?, ?)', (new_id(), row['tag_id'], 'person', person_id, now_iso()))
            self.connection.execute('UPDATE people SET tags=? WHERE id=?', (json.dumps(list(dict.fromkeys(row['name'] for row in rows))), person_id))
