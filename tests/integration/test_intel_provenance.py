import pytest
from netops.domain.validation import UserInputError
from netops.services.app_backend import NetworkOpsBackend


def test_intel_provenance_edits_preserve_original(v1_repository):
    b = NetworkOpsBackend(v1_repository)
    p = b.create_person({'name':'Fictional researcher'})['person_id']
    original = b.people.add_signal(p, text='Legacy signal', source_description='Original document')
    row = b.get_dossier(p)['folder_payloads']['signals'][0]
    assert row['date'] is None and row['origin'] is None and row['intel_type'] == 'Signal'
    updated = b.update_intel(original.signal_id, {'text':'Corrected interpretation','intel_type':'Inference','revision':1,'event_date':'2022-03-04','origin':'Document'})
    assert updated['id'] == original.signal_id and updated['created_at'] == original.created_at
    assert updated['event_date'] == '2022-03-04'
    history = b.intelligence.history(original.signal_id)
    assert history[0]['signal_text'] == 'Legacy signal' and history[0]['origin'] is None
    with pytest.raises(UserInputError, match='changed'):
        b.update_intel(original.signal_id, {'text':'Stale correction','revision':1})
    created = b.add_signal(p, {'text':'New observation', 'intel_type':'Observation','source_date':'2021-04-05'})
    assert created['origin'] == 'User' and created['creator'] == 'Isaac Wanlemvo'
    with pytest.raises(UserInputError):
        b.add_signal(p, {'text':'Wrong interaction', 'source_interaction_id':'missing'})
