import json
from netops.services.app_backend import NetworkOpsBackend
from netops.storage import NetOpsRepository, connect
from netops.storage.migrations import MIGRATIONS, migrate


def test_catalog_migrates_union_without_erasing_legacy_data(tmp_path):
    c = connect(tmp_path / 'legacy.sqlite3')
    c.execute('CREATE TABLE schema_version(version INTEGER PRIMARY KEY)')
    for version, script in MIGRATIONS:
        if version > 6: break
        c.executescript(script)
        c.execute('INSERT INTO schema_version VALUES (?)', (version,)); c.commit()
    c.execute("INSERT INTO people(id,person_id,display_name,name,tags,created_at,updated_at) VALUES ('p','p','Fictional','Fictional',?,'2020','2020')", (json.dumps(['  Space   Club ', 'space club']),))
    c.execute("INSERT INTO tags VALUES ('old','SPACE CLUB','space club','2020','2020',NULL)")
    c.execute("INSERT INTO tags VALUES ('extra','Research','research','2020','2020',NULL)")
    c.execute("INSERT INTO taggings VALUES ('g','extra','person','p','2020')"); c.commit()
    migrate(c)
    backend = NetworkOpsBackend(NetOpsRepository(c))
    assert backend.get_person('p')['tags'] == ['Research', 'SPACE CLUB']
    assert json.loads(c.execute("SELECT tags FROM people WHERE id='p'").fetchone()[0]) == ['  Space   Club ', 'space club']
    assert c.execute("SELECT tag_id FROM tags WHERE tag_id='old'").fetchone()
    assert backend.repository.save_catalog_tag('Space  club')['tag_id'] == 'old'
    backend.update_person('p', {'tags':['Research']})
    assert backend.get_person('p')['tags'] == ['Research']
    assert json.loads(c.execute("SELECT tags FROM people WHERE id='p'").fetchone()[0]) == ['Research']
    c.close()


def test_custom_vocabularies_persist_and_normalize(v1_repository):
    first = v1_repository.save_type('relationship', ' Study   Partner ')
    assert v1_repository.save_type('relationship', 'study partner')['type_id'] == first['type_id']
    assert v1_repository.save_type('interaction', 'Working   Session')['type_id'] == v1_repository.save_type('interaction', 'working session')['type_id']
    assert {'Friend','Coworker'} <= {t['label'] for t in v1_repository.catalog()['relationship']}
