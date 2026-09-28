from __future__ import annotations

from netops.domain.models import Interaction, Person, PersonContact, Relationship
from netops.storage import NetOpsRepository, connect


def test_v1_migration_preserves_existing_person_and_contact_data(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(
        Person(
            display_name="Henry Valentine",
            primary_email="henry@example.com",
            primary_phone="555-0100",
            organization="T-Mobile",
            relationship_strength="high",
        )
    )
    repository.add_person_contact(
        PersonContact(person_id=person.id, kind="linkedin", label="profile", value="https://linkedin.example/henry")
    )

    saved = repository.get_v1_person(person.id)
    contacts = repository.list_contact_methods(person.id)

    assert saved.person_id == person.id
    assert saved.name == "Henry Valentine"
    assert {contact.type for contact in contacts} >= {"email", "phone", "linkedin"}


def test_v1_migration_maps_existing_interactions_and_relationships(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    henry = repository.add_person(Person(display_name="Henry Valentine"))
    isaac = repository.add_person(Person(display_name="Isaac"))
    interaction = repository.add_interaction(
        Interaction(person_id=henry.id, interaction_type="meeting", notes="Discussed persistence.")
    )
    repository.add_relationship(
        Relationship(person_id=henry.id, related_person_id=isaac.id, relationship_type="mentors", notes="Career help")
    )

    linked_interactions = repository.list_v1_interactions_for_person(henry.id)
    links = repository.list_relationship_links_for_entity("person", henry.id)

    assert linked_interactions[0].interaction_id == interaction.id
    assert linked_interactions[0].summary == "Discussed persistence."
    assert links[0].relationship_type == "mentors"
