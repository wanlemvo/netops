from __future__ import annotations

import sqlite3

import pytest

from netops.domain.validation import UserInputError
from netops.storage.migrations import MIGRATIONS
from netops.services import PeopleService
from netops.storage import NetOpsRepository, connect


def test_existing_version_one_people_become_valid_dossiers(tmp_path):
    db_path = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.executescript(MIGRATIONS[0][1])
    connection.execute("INSERT INTO schema_version(version, applied_at) VALUES (1, CURRENT_TIMESTAMP)")
    connection.execute(
        "INSERT INTO people (id, display_name, tags, created_at, updated_at) VALUES ('p1', 'Avery Chen', '[]', '2026-01-01', '2026-01-01')"
    )
    connection.commit()
    connection.close()

    repository = NetOpsRepository(connect(db_path))
    dossier = repository.dossier("p1")
    assert dossier.person.display_name == "Avery Chen"
    assert dossier.person.interests == []
    assert dossier.raw_notes == []


def test_unknown_editable_field_does_not_mutate_person(isolated_db):
    service = PeopleService(NetOpsRepository(connect(isolated_db)))
    person = service.create_person(name="Avery Chen", role="Founder")
    with pytest.raises(UserInputError):
        service.update_profile_field(person.id, "network_score", "99")
    assert service.resolve_person(person.id).role == "Founder"


def test_raw_notes_are_append_only_and_ordered(isolated_db):
    service = PeopleService(NetOpsRepository(connect(isolated_db)))
    person = service.create_person(name="Avery Chen")
    service.append_raw_note(person.id, "First raw note")
    service.append_raw_note(person.id, "Second raw note")
    dossier = service.dossier(person.id)
    assert [note.note for note in dossier.raw_notes] == ["First raw note", "Second raw note"]
