"""Intel provenance and narrowly scoped content revisions."""
import json
from datetime import date

from netops.domain.models import Signal, new_id, now_iso
from netops.domain.validation import NotFoundError, UserInputError, normalize_date_text, normalize_optional_text

INTEL_TYPES = ('Fact', 'Observation', 'Signal', 'Inference', 'Unknown')
ORIGINS = ('User', 'Interaction', 'Web', 'AI', 'Document', 'System', 'Other')


class IntelligenceService:
    def __init__(self, repository, people):
        self.repository, self.people = repository, people

    def save(self, person_query, payload, signal_id=None):
        person = self.people.get_v1_person(person_query)
        c = self.repository.connection
        with c:
            old = c.execute('SELECT * FROM signals WHERE signal_id=? AND person_id=? AND archived_at IS NULL', (signal_id, person.person_id)).fetchone() if signal_id else None
            if signal_id and old is None:
                raise NotFoundError('Intel record was not found.')
            before = dict(old) if old else {}
            if old and int(payload.get('revision', -1)) != old['revision']:
                raise UserInputError('This Intel changed. Reopen it before saving.')
            values = {**before, **{key: payload[key] for key in ('intel_type','event_date','source_date','origin','creator','confidence','source_interaction_id','source_description') if key in payload}}
            values.update(person_id=person.person_id, signal_text=payload.get('text', payload.get('signal_text', before.get('signal_text', ''))))
            if not old:
                values.update(intel_type=payload.get('intel_type') or 'Signal', origin=payload.get('origin') or 'User', creator=payload.get('creator') or 'Isaac Wanlemvo', event_date=payload.get('event_date', date.today().isoformat()))
            if values.get('intel_type') not in INTEL_TYPES:
                raise UserInputError('Choose a supported Intel type.')
            if values.get('origin') not in (*ORIGINS, None, ''):
                raise UserInputError('Choose a supported origin.')
            for key in ('event_date','source_date'):
                values[key] = normalize_date_text(values.get(key))
            for key in ('source_interaction_id','source_description','creator','origin','confidence'):
                values[key] = normalize_optional_text(values.get(key))
            if values.get('source_interaction_id') and not c.execute('SELECT 1 FROM interaction_people WHERE interaction_id=? AND person_id=?', (values['source_interaction_id'], person.person_id)).fetchone():
                raise UserInputError('The related interaction must include this person.')
            values['updated_at'] = now_iso()
            values['revision'] = before.get('revision', 0) + 1
            signal = Signal.model_validate(values)
            if old:
                c.execute('INSERT INTO intel_revisions VALUES (?, ?, ?, ?, ?)', (new_id(), signal_id, old['revision'], json.dumps(before), signal.updated_at))
            else:
                self.repository.add_signal(signal)
            data = signal.model_dump()
            columns = ('signal_text','confidence','source_interaction_id','source_description','intel_type','event_date','source_date','origin','creator','revision','updated_at')
            c.execute('UPDATE signals SET ' + ','.join(f'{key}=?' for key in columns) + ' WHERE signal_id=?', tuple(data[key] for key in columns) + (signal.signal_id,))
        return signal

    def history(self, signal_id):
        if not self.repository.connection.execute('SELECT 1 FROM signals WHERE signal_id=?', (signal_id,)).fetchone():
            raise NotFoundError('Intel record was not found.')
        return [json.loads(row[0]) for row in self.repository.connection.execute('SELECT snapshot FROM intel_revisions WHERE signal_id=? ORDER BY revision DESC', (signal_id,))]
