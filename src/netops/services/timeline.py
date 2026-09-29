"""Read-only chronology derived from structured records, never imported prose."""
import json


def derive_timeline(repository, person_id, interactions, intel, relationships):
    result = []
    for item in interactions:
        result.append({**item, 'event_id':'interaction:' + item['id'], 'date':item['date'] or item['created_at'][:10],
            'date_basis':'Event' if item['date'] else 'Recorded — event date unknown', 'sort_date':item['date'] or item['created_at']})
    for item in intel:
        result.append({**item, 'event_id':'intel:' + item['id'], 'date':item['date'] or item['created_at'][:10],
            'title':item['intel_type'] + ' added', 'summary':item['text']})
        for row in repository.connection.execute('SELECT revision_id, recorded_at FROM intel_revisions WHERE signal_id=?', (item['id'],)):
            result.append({'event_id':'intel-revision:' + row['revision_id'], 'kind':'intel_revision', 'title':'Intel corrected',
                'summary':'Earlier content and provenance preserved in Intel history.', 'date':row['recorded_at'][:10], 'sort_date':row['recorded_at'], 'date_basis':'Recorded'})
    for item in relationships:
        who = item['source_label'] + ' → ' + item['target_label']
        for field, verb in [('started_on','started'), ('ended_on','ended')]:
            when = item.get(field)
            if field == 'ended_on' and not when: continue
            result.append({'event_id':'relationship:' + item['id'] + ':' + field, 'kind':'relationship',
                'title':item['relationship_type'] + (' ' + verb if when else ' recorded'), 'summary':who,
                'date':when or item['created_at'][:10], 'sort_date':when or item['created_at'],
                'date_basis':('Event (month)' if len(when) == 7 else 'Event') if when else 'Recorded — start unknown'})
    for row in repository.connection.execute('SELECT * FROM follow_up_completions'):
        if person_id not in json.loads(row['person_ids']): continue
        result.append({'event_id':'completion:' + row['event_id'], 'kind':'follow_up_completion', 'title':'Follow-up completed',
            'summary':row['action'] or 'Completed action', 'date':row['completed_at'][:10], 'sort_date':row['completed_at'],
            'date_basis':'Completed', 'scheduled_date':row['scheduled_date']})
    return sorted(result, key=lambda r:(r.get('sort_date') or '', r['event_id']), reverse=True)
