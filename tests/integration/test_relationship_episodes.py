import pytest
from netops.domain.validation import UserInputError
from netops.services.app_backend import NetworkOpsBackend
from netops.storage import NetOpsRepository, connect


def test_simultaneous_types_end_independently_and_restart_preserves_history(tmp_path):
    db = tmp_path / 'episodes.sqlite3'
    b = NetworkOpsBackend(NetOpsRepository(connect(db)))
    p, q = [b.create_person({'name':name})['person_id'] for name in ['Fictional A','Fictional B']]
    common = dict(source_person_id=p,target_person_id=q)
    coworker = b.add_relationship_link({**common,'relationship_type':'Coworker','started_on':'2024-09'})
    friend = b.add_relationship_link({**common,'relationship_type':'Friend','started_on':'2025-03'})
    assert len(b.get_dossier(p)['connections']) == 2
    ended = b.update_relationship(friend['id'], {'ended_on':'2025-09','revision':1})
    assert ended['status'] == 'Ended'
    connections = {r['id']:r for r in b.get_dossier(q)['connections']}
    assert connections[coworker['id']]['status'] == 'Active'
    assert connections[friend['id']]['started_on'] == '2025-03'
    assert b.relationships.history(friend['id'])[0]['ended_on'] is None
    new_friend = b.add_relationship_link({**common,'relationship_type':'friend','started_on':'2026-01'})
    assert new_friend['id'] != friend['id']
    with pytest.raises(UserInputError, match='already active'):
        b.add_relationship_link({**common,'relationship_type':' FRIEND '})
    with pytest.raises(UserInputError, match='ended episode'):
        b.update_relationship(friend['id'], {'ended_on':None,'revision':2})
    with pytest.raises(UserInputError, match='precede'):
        b.update_relationship(new_friend['id'], {'ended_on':'2024-01','revision':1})
    b.repository.connection.close()
    restored = NetworkOpsBackend(NetOpsRepository(connect(db)))
    assert len(restored.get_dossier(p)['connections']) == 3
    assert len(restored.relationships.history(friend['id'])) == 1
    restored.repository.connection.close()
