from __future__ import annotations

from netops.domain.models import Person
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

