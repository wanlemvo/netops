"""One row per typed relationship episode, independent of simultaneous types."""
import json
from datetime import date

from netops.domain.models import RelationshipLink, new_id, now_iso
from netops.domain.validation import NotFoundError, UserInputError, normalize_date_text
from netops.storage.catalog import normalized


class RelationshipService:
    def __init__(self, repository, people):
        self.repository, self.people = repository, people

    def save(self, payload, link_id=None):
        c = self.repository.connection
        with c:
            old = c.execute('SELECT * FROM relationship_links WHERE relationship_link_id=? AND archived_at IS NULL', (link_id,)).fetchone() if link_id else None
            if link_id and old is None:
                raise NotFoundError('Relationship was not found.')
            if old:
                if int(payload.get('revision', -1)) != old['revision']:
                    raise UserInputError('This relationship changed. Reopen it before saving.')
                values = dict(old)
                for key in ('description','started_on','ended_on'):
                    if key in payload: values[key] = payload[key]
                if old['ended_on'] and not values.get('ended_on'):
                    raise UserInputError('Keep the ended episode. Add a new relationship to start it again.')
            else:
                source = self.people.get_v1_person(str(payload.get('source_person_id') or payload.get('source') or ''))
                target = self.people.get_v1_person(str(payload.get('target_person_id') or payload.get('target') or ''))
                if source.person_id == target.person_id:
                    raise UserInputError('Choose two different people.')
                label = self.repository.save_type('relationship', payload.get('relationship_type') or payload.get('type'))['label']
                values = dict(source_entity_type='person', source_entity_id=source.person_id, target_entity_type='person', target_entity_id=target.person_id,
                    relationship_type=label, description=payload.get('description'), started_on=payload.get('started_on', date.today().isoformat()), ended_on=payload.get('ended_on'))
            for key in ('started_on','ended_on'):
                values[key] = normalize_date_text(values.get(key), allow_month=True, label=key.replace('_',' '))
            if values['started_on'] and values['ended_on']:
                start = values['started_on'] + ('-01' if len(values['started_on']) == 7 else '')
                end = values['ended_on'] + ('-31' if len(values['ended_on']) == 7 else '')
                if end < start: raise UserInputError('End date cannot precede start date.')
            if not old and not values['ended_on']:
                active = c.execute("SELECT relationship_type FROM relationship_links WHERE source_entity_id=? AND target_entity_id=? AND source_entity_type='person' AND target_entity_type='person' AND ended_on IS NULL AND archived_at IS NULL", (values['source_entity_id'], values['target_entity_id']))
                if any(normalized(row[0]) == normalized(values['relationship_type']) for row in active):
                    raise UserInputError('This relationship type is already active between these people.')
            values['updated_at'] = now_iso()
            values['revision'] = old['revision'] + 1 if old else 1
            link = RelationshipLink.model_validate(values)
            if old:
                c.execute('INSERT INTO relationship_revisions VALUES (?, ?, ?, ?, ?)', (new_id(), link_id, old['revision'], json.dumps(dict(old)), link.updated_at))
            else:
                self.repository.add_relationship_link(link)
            c.execute('UPDATE relationship_links SET started_on=?,ended_on=?,description=?,revision=?,updated_at=? WHERE relationship_link_id=?', (link.started_on,link.ended_on,link.description,link.revision,link.updated_at,link.relationship_link_id))
        return link

    def history(self, link_id):
        if not self.repository.connection.execute('SELECT 1 FROM relationship_links WHERE relationship_link_id=?', (link_id,)).fetchone():
            raise NotFoundError('Relationship was not found.')
        return [json.loads(r[0]) for r in self.repository.connection.execute('SELECT snapshot FROM relationship_revisions WHERE relationship_link_id=? ORDER BY revision DESC', (link_id,))]
