from __future__ import annotations

from datetime import date, timedelta

import pytest

from netops.domain.validation import UserInputError
from netops.services import InteractionService, PeopleService
from netops.storage import NetOpsRepository, connect


def make_people_service(db_path):
    repository = NetOpsRepository(connect(db_path))
    return PeopleService(repository)


def test_create_person_requires_only_name(isolated_db):
    service = make_people_service(isolated_db)
    person = service.create_person(name="Avery Chen")
    dossier = service.dossier(person.id)
    assert dossier.person.display_name == "Avery Chen"
    assert dossier.person.role is None
    assert dossier.raw_notes == []


def test_update_profile_field_preserves_unrelated_fields(isolated_db):
    service = make_people_service(isolated_db)
    person = service.create_person(name="Avery Chen", organization="Northwind", role="Founder")
    updated = service.update_profile_field(person.id, "relationship_strength", "High")
    assert updated.relationship_strength == "high"
    assert updated.organization == "Northwind"
    assert updated.role == "Founder"


def test_update_profile_field_rejects_invalid_strength(isolated_db):
    service = make_people_service(isolated_db)
    person = service.create_person(name="Avery Chen")
    with pytest.raises(UserInputError):
        service.update_profile_field(person.id, "relationship_strength", "excellent")


def test_grouped_directory_rows_adds_headers(isolated_db):
    service = make_people_service(isolated_db)
    service.create_person(name="Avery Chen")
    service.create_person(name="3M Contact")
    rows = service.grouped_directory_rows()
    assert [row["name"] for row in rows if row.get("kind") == "header"] == ["#", "A"]


def test_dossier_last_contact_comes_from_latest_interaction(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    people = PeopleService(repository)
    interactions = InteractionService(repository, people)
    person = people.create_person(name="Avery Chen")
    interactions.log_interaction(person.id, occurred_on=date.today() - timedelta(days=5), interaction_type="email", notes="Older")
    interactions.log_interaction(person.id, occurred_on=date.today(), interaction_type="call", notes="Newest")
    dossier = people.dossier(person.id)
    assert dossier.last_contact == date.today()
    assert dossier.recent_interactions[0].notes == "Newest"
