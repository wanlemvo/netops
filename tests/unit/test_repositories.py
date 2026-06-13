from __future__ import annotations

import pytest

from netops.domain.models import ContactMethod, Person, RelationshipLink, V1Person
from netops.domain.validation import UserInputError
from netops.storage import NetOpsRepository, connect


def test_migration_creates_schema(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    repository.add_person(Person(display_name="Avery Chen"))
    people = repository.list_people()
    assert people[0].display_name == "Avery Chen"


def test_repository_round_trips_tags(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(Person(display_name="Avery Chen", tags=["mentor", "northwind"]))
    saved = repository.get_person(person.id)
    assert saved.tags == ["mentor", "northwind"]


def test_v1_repository_uses_uuid_identity_and_archive_fields(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_v1_person(V1Person(name="Avery Chen", archived_at="2026-06-10T00:00:00"))

    saved = repository.get_v1_person(person.person_id)

    assert saved.person_id == person.person_id
    assert saved.name == "Avery Chen"
    assert saved.archived_at == "2026-06-10T00:00:00"


def test_v1_relationship_link_rejects_unknown_entity_type(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))

    with pytest.raises(UserInputError):
        repository.add_relationship_link(
            RelationshipLink(
                source_entity_type="note",
                source_entity_id="source",
                target_entity_type="person",
                target_entity_id="target",
                relationship_type="mentions",
            )
        )


def test_v1_contact_methods_crud_and_primary_selection(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_v1_person(V1Person(name="Henry Valentine"))
    email = repository.add_contact_method(
        ContactMethod(person_id=person.person_id, type="email", label="work", value="Henry@Example.COM")
    )
    phone = repository.add_contact_method(
        ContactMethod(person_id=person.person_id, type="phone", label="mobile", value="555-0100")
    )

    contacts = repository.list_contact_methods(person.person_id)
    assert [contact.normalized_value for contact in contacts] == ["henry@example.com", "555-0100"]

    primary = repository.set_primary_contact_method(phone.contact_method_id)
    assert primary.is_primary == 1

    repository.delete_contact_method(email.contact_method_id)
    remaining = repository.list_contact_methods(person.person_id)
    assert [contact.contact_method_id for contact in remaining] == [phone.contact_method_id]
