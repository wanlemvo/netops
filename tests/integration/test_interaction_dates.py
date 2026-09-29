import pytest
from netops.services.app_backend import NetworkOpsBackend
from netops.domain.validation import UserInputError


def test_multi_participant_empty_summary_and_invalid_legacy_date(v1_repository):
    b = NetworkOpsBackend(v1_repository)
    people = [b.create_person({'name': name})['person_id'] for name in ['Fictional A','Fictional B']]
    interaction = b.add_interaction({'people':people, 'interaction_date':'2021-02-03','interaction_type':'Call'})
    assert len(b.get_overview()['recent_intel']) == 1
    for person in people:
        item = b.get_dossier(person)['folder_payloads']['interactions'][0]
        assert item['date'] == '2021-02-03'
        assert len(item['participants']) == 2
        assert item['created_at'] != item['date']
    with pytest.raises(UserInputError):
        b.add_interaction({'people':people, 'interaction_date':''})
    with pytest.raises(UserInputError):
        b.add_interaction({'people':people, 'interaction_date':'invalid'})
    with v1_repository.connection:
        v1_repository.connection.execute('UPDATE interactions SET interaction_date=?,occurred_on=? WHERE id=?', ('invalid original','invalid original',interaction['interaction_id']))
    assert b.get_dossier(people[0])['folder_payloads']['interactions'][0]['date'] is None
    assert v1_repository.connection.execute('SELECT interaction_date FROM interactions').fetchone()[0] == 'invalid original'


def test_unrelated_person_edit_preserves_invalid_legacy_date(v1_repository):
    b = NetworkOpsBackend(v1_repository)
    pid = b.create_person({'name':'Fictional historical record'})['person_id']
    with v1_repository.connection:
        v1_repository.connection.execute('UPDATE people SET first_met=? WHERE id=?', ('spring, uncertain',pid))
    b.update_person(pid, {'organization':'Fictional Lab'})
    assert v1_repository.connection.execute('SELECT first_met FROM people WHERE id=?', (pid,)).fetchone()[0] == 'spring, uncertain'
    assert b.get_person(pid)['first_met'] is None
