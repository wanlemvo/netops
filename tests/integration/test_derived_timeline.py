from netops.services.app_backend import NetworkOpsBackend


def test_timeline_separates_source_dates_and_preserves_completion_cycles(v1_repository):
    b = NetworkOpsBackend(v1_repository)
    p = b.create_person({'name':'Fictional A','dossier':'Met in 2014, perhaps.','next_action':'Send outline'})['person_id']
    q = b.create_person({'name':'Fictional B'})['person_id']
    b.add_interaction({'people':[p,q],'interaction_date':'2021-01-01','summary':'Confirmed meeting'})
    legacy = b.people.add_signal(p,text='Old undated observation')
    b.add_relationship_link({'source_person_id':p,'target_person_id':q,'relationship_type':'Friend','started_on':'2022-03'})
    b.complete_follow_up('person', p)
    b.complete_follow_up('person', p)
    b.reschedule_follow_up('person', p, {'follow_up_date':'2030-01-01'})
    b.update_person(p, {'next_action':'Second action'})
    b.complete_follow_up('person', p)
    timeline = b.get_dossier(p)['timeline']
    assert not any('2014' in str(item) for item in timeline)
    assert next(item for item in timeline if item.get('id') == legacy.signal_id)['date_basis'] == 'Recorded'
    assert next(item for item in timeline if item['title'] == 'Friend started')['date'] == '2022-03'
    completed = [item for item in timeline if item['kind'] == 'follow_up_completion']
    assert len(completed) == 2
    assert {item['summary'] for item in completed} == {'Send outline','Second action'}
    assert len({item['event_id'] for item in timeline}) == len(timeline)
