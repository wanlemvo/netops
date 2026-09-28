import json
import shutil
import sqlite3
import urllib.request
import urllib.error

import pytest

from netops.services.app_backend import NetworkOpsBackend
from netops.storage import NetOpsRepository, connect
from netops.storage.migrations import MIGRATIONS, current_version
from netops.gui.server import NetOpsGuiServer
from netops.domain.validation import UserInputError


def backend(path):
    return NetworkOpsBackend(NetOpsRepository(connect(path)))


def test_follow_up_lifecycle_and_reopen(isolated_db):
    app = backend(isolated_db)
    person = app.create_person({'name': 'Avery Fiction', 'next_action': 'Send outline', 'interests': 'Woodwork', 'tags': ['demo']})
    pid = person['person_id']
    interaction = app.add_interaction({'people': [pid], 'summary': 'Planning session', 'follow_up_date': '2030-01-02'})
    unscheduled = app.add_interaction({'people': [pid], 'summary': 'Check in', 'follow_up_required': True})
    opportunity = app.add_opportunity({'people': [pid], 'title': 'Workshop', 'follow_up_date': '2030-01-03'})
    assert interaction['follow_up_required']
    pending = app.review_followups()
    assert len(pending) == 4
    for row in pending:
        first = app.complete_follow_up(row['kind'], row['id'])
        assert first == app.complete_follow_up(row['kind'], row['id'])
    assert app.review_followups() == []
    assert app.get_dossier(pid)['folder_payloads']['opportunities'][0]['status'] == 'open'
    app.update_person(pid, {'organization': 'Fictional Studio', 'tags': ['updated']})
    assert app.review_followups() == []
    assert app.get_person(pid)['interests'] == 'Woodwork'
    app.update_person(pid, {'next_action': 'Send a revised outline'})
    app.reschedule_follow_up('interaction', interaction['interaction_id'], {'follow_up_date': '2030-02-02'})
    app.reschedule_follow_up('opportunity', opportunity['id'], {'follow_up_date': '2030-02-03'})
    app.repository.connection.close()
    reopened = backend(isolated_db)
    assert len(reopened.review_followups()) == 3
    records = reopened.get_dossier(pid)['folder_payloads']['interactions']
    assert any(x['id'] == unscheduled['interaction_id'] and x['follow_up_completed_at'] for x in records)
    reopened.repository.connection.close()


def test_invalid_edits_and_nested_writes_are_atomic(isolated_db, monkeypatch):
    app = backend(isolated_db)
    person = app.create_person({'name': 'Original Fiction', 'dossier': 'First\nSecond'})
    with pytest.raises(UserInputError):
        app.update_person(person['person_id'], {'name': 'Changed', 'follow_up_date': 'not-a-date'})
    assert app.get_person(person['person_id'])['name'] == 'Original Fiction'
    def fail(*args):
        raise RuntimeError('Simulated contact failure')
    monkeypatch.setattr(app, '_create_inline_contact_methods', fail)
    with pytest.raises(RuntimeError):
        app.create_person({'name': 'Must roll back'})
    with pytest.raises(RuntimeError):
        app.update_person(person['person_id'], {'name': 'Must roll back'})
    assert len(app.list_people()) == 1
    assert app.get_person(person['person_id'])['name'] == 'Original Fiction'
    app.repository.connection.close()


def test_v4_migration_recovers_dated_interaction_without_losing_rows(tmp_path):
    path = tmp_path / 'old.sqlite3'
    c = sqlite3.connect(path)
    c.executescript('CREATE TABLE schema_version(version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP);')
    for version, sql in MIGRATIONS:
        if version >= 5: break
        c.executescript(sql)
        c.execute('INSERT INTO schema_version(version) VALUES (?)', (version,))
        c.commit()
    c.close()
    # Build representative old records with the current repository, then restore v4 shape in a fixture copy.
    app = backend(path)
    pid = app.create_person({'name': 'Migration Fiction', 'dossier': 'Preserve\nall lines'})['person_id']
    record = app.add_interaction({'people': [pid], 'summary': 'Historical summary', 'follow_up_date': '2030-04-05'})
    c = app.repository.connection
    with c:
        for trigger in ['reopen_person_follow_up', 'reopen_interaction_follow_up', 'reopen_opportunity_follow_up']:
            c.execute(f'DROP TRIGGER {trigger}')
        for table in ['people', 'interactions', 'opportunities']:
            c.execute(f'ALTER TABLE {table} DROP COLUMN follow_up_completed_at')
        c.execute('DELETE FROM schema_version WHERE version = 5')
        c.execute('UPDATE interactions SET follow_up_required = 0')
    before = c.execute('SELECT summary, follow_up_date FROM interactions').fetchall()
    c.close()
    migrated = backend(path)
    assert current_version(migrated.repository.connection) == 5
    after = migrated.repository.connection.execute('SELECT summary, follow_up_date FROM interactions').fetchall()
    assert [tuple(x) for x in before] == [tuple(x) for x in after]
    assert migrated.get_person(pid)['dossier'] == 'Preserve\nall lines'
    assert migrated.review_followups()[0]['id'] == record['interaction_id']
    assert migrated.repository.connection.execute('PRAGMA foreign_key_check').fetchall() == []
    migrated.repository.connection.close()


def test_moved_photo_and_api_completion(tmp_path):
    source = tmp_path / 'Original root'
    path = source / 'data/netops.sqlite3'
    app = backend(path)
    pid = app.create_person({'name': 'Photo Fiction', 'next_action': 'Send photo'})['person_id']
    photo = tmp_path / 'fiction.png'
    photo.write_bytes(b'fictional image')
    app.people.set_profile_photo(pid, str(photo))
    app.repository.connection.close()
    moved = tmp_path / 'Renamed portable root'
    shutil.move(str(source), moved)
    path = moved / 'data/netops.sqlite3'
    server = NetOpsGuiServer(backend_factory=lambda: backend(path))
    server.start_background()
    try:
        with urllib.request.urlopen(f'{server.url}api/people/{pid}/profile-photo') as response:
            assert response.read() == b'fictional image'
        request = urllib.request.Request(f'{server.url}api/follow-ups/person/{pid}/complete', data=b'{}', headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request) as response:
            assert json.load(response)['completed_at']
        request = urllib.request.Request(f'{server.url}api/follow-ups/person/missing/complete', data=b'{}', headers={'Content-Type': 'application/json'})
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        assert error.value.code == 404
    finally:
        server.stop()
