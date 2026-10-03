"""Opt-in fictional data; never loaded by normal application startup."""
import argparse
from pathlib import Path

from netops.services.app_backend import NetworkOpsBackend
from netops.storage import NetOpsRepository, connect


def seed_demo(path: Path) -> None:
    if path.exists():
        raise ValueError('Demo destination already exists. Choose a new database path.')
    app = NetworkOpsBackend(NetOpsRepository(connect(path)))
    try:
        a = app.create_person({'name': 'Avery Chen', 'role': 'Community designer', 'organization': 'Northstar Fieldworks',
            'location': 'Portland', 'dossier': '# Background\nFictional demo contact. Designs **accessible neighborhood workshops**.\n\n## Working preferences\n- Practical examples\n- Small groups\n- Written agendas',
            'tags': ['Community', 'Design'], 'origin_story': 'Met through a fictional workshop planning group.', 'first_met': '2024-09',
            'current_goals': 'Plan an autumn workshop\nFind a venue', 'preferences': 'Concise email agendas',
            'communication_style': 'Thoughtful and direct', 'potential_value': 'Community partnerships',
            'relationship_type': 'collaborator', 'relationship_status': 'active', 'next_action': 'Share the workshop outline',
            'follow_up_date': '2030-10-02'})
        b = app.create_person({'name': 'Morgan Ellis', 'role': 'Program coordinator', 'organization': 'Cedar Studio',
            'dossier': 'Fictional demo contact. Coordinates practical learning events.', 'location': 'Seattle'})
        pid = a['person_id']
        app.add_contact_method(pid, {'type': 'email', 'value': 'avery@example.com'})
        app.add_interaction({'people': [pid, b['person_id']], 'interaction_date': '2026-09-20', 'interaction_type': 'planning meeting',
            'summary': 'Discussed a small community workshop.\nAgreed to share a draft agenda.', 'action_items': 'Send draft agenda', 'follow_up_date': '2030-10-03'})
        app.add_signal(pid, {'text': 'Prefers practical examples and small groups.', 'intel_type':'Observation', 'event_date':'2026-09-20', 'confidence': 'high', 'source_description': 'Fictional demo conversation'})
        app.add_opportunity({'people': [pid], 'title': 'Neighborhood workshop', 'description': 'A fictional joint learning event.', 'follow_up_date': '2030-10-08'})
        app.add_relationship_link({'source_person_id': pid, 'target_person_id': b['person_id'], 'relationship_type': 'collaborator', 'started_on':'2024-09'})
    finally:
        app.repository.connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    args = parser.parse_args()
    seed_demo(args.database.resolve())
    print(f'Fictional demo created: {args.database.resolve()}')


if __name__ == '__main__':
    main()
