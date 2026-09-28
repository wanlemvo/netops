from __future__ import annotations

from netops.domain.models import Person, RawNoteEntry
from netops.storage import NetOpsRepository, connect


def test_person_notes_append_without_replacing_existing_notes(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(Person(display_name="Avery Chen"))
    first = repository.add_person_note(RawNoteEntry(person_id=person.id, note="First note"))
    second = repository.add_person_note(RawNoteEntry(person_id=person.id, note="Second note"))
    notes = repository.list_person_notes(person.id)
    assert [note.id for note in notes] == [first.id, second.id]
    assert [note.note for note in notes] == ["First note", "Second note"]


def test_repository_round_trips_dossier_fields(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(
        Person(
            display_name="Avery Chen",
            alias="Ace",
            role="Founder",
            relationship_strength="medium",
            interests=["systems", "coffee"],
            signals=["hiring"],
        )
    )
    saved = repository.get_person(person.id)
    assert saved.alias == "Ace"
    assert saved.role == "Founder"
    assert saved.interests == ["systems", "coffee"]
    assert saved.signals == ["hiring"]
