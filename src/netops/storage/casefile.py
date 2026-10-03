"""Storage for editable case-file sections; original imported dossier text is retained."""
from netops.domain.models import new_id, now_iso
from netops.domain.validation import NotFoundError, UserInputError


class CasefileRepository:
    def list_dossier_sections(self, person_id):
        return [dict(row) for row in self.connection.execute(
            'SELECT * FROM dossier_sections WHERE person_id = ? ORDER BY created_at, section_id', (person_id,))]

    def save_dossier_section(self, person_id, section_id, title, body, original=None, expected_revision=None, format='plain'):
        with self.connection:
            row = self.connection.execute('SELECT * FROM dossier_sections WHERE section_id = ? AND person_id = ?', (section_id, person_id)).fetchone()
            previous = dict(row) if row else original
            if expected_revision is not None and int(expected_revision) != (previous or {}).get('revision', 0):
                raise UserInputError('This section changed since it was opened. Reopen it before saving.')
            stamp = now_iso()
            revision = previous['revision'] + 1 if previous else 1
            self.connection.execute('''INSERT INTO dossier_sections(section_id, person_id, title, body, format, revision, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(section_id) DO UPDATE SET title=excluded.title, body=excluded.body, format=excluded.format, revision=excluded.revision, updated_at=excluded.updated_at''',
                (section_id, person_id, title, body, format, revision, (previous or {}).get('created_at') or stamp, stamp))
            if previous:
                self.connection.execute('INSERT INTO dossier_revisions VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (new_id(), section_id, previous['title'], previous['body'], previous['format'], previous['revision'], stamp))
        return next(row for row in self.list_dossier_sections(person_id) if row['section_id'] == section_id)

    def dossier_section_history(self, person_id, section_id):
        if not self.connection.execute('SELECT 1 FROM dossier_sections WHERE section_id=? AND person_id=?', (section_id, person_id)).fetchone():
            raise NotFoundError('No saved section history was found.')
        return [dict(row) for row in self.connection.execute('SELECT * FROM dossier_revisions WHERE section_id=? ORDER BY revision DESC', (section_id,))]
