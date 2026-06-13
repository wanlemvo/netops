from __future__ import annotations

import os

import pytest


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    db_path = tmp_path / "netops.sqlite3"
    monkeypatch.setenv("NETOPS_DB", str(db_path))
    return db_path


@pytest.fixture()
def runner(isolated_db):
    from typer.testing import CliRunner

    return CliRunner()


@pytest.fixture()
def v1_repository(isolated_db):
    from netops.storage import NetOpsRepository, connect

    return NetOpsRepository(connect(isolated_db))


@pytest.fixture()
def fake_tui_services():
    from dataclasses import dataclass, field

    from netops.domain.models import DashboardSummary, Dossier, Person

    @dataclass
    class FakePeople:
        rows: list[dict[str, str]] = field(default_factory=list)
        created: list[Person] = field(default_factory=list)

        def directory_rows(self):
            return self.rows + [
                {
                    "id": person.id,
                    "name": person.display_name,
                    "organization": person.organization or "",
                    "tags": ", ".join(person.tags),
                    "last_interaction": "",
                    "open_loops": "0",
                }
                for person in self.created
            ]

        def dashboard(self):
            return DashboardSummary(total_people=len(self.directory_rows()))

        def create_person(self, *, name, organization=None, tags=None, notes=None, **_):
            person = Person(display_name=name, organization=organization, tags=tags or [], relationship_notes=notes)
            self.created.append(person)
            return person

        def create_v1_person(self, *, name, organization=None, tags=None, **_):
            person = Person(display_name=name, organization=organization, tags=tags or [])
            self.created.append(person)
            return person

        @property
        def repository(self):
            return self

        def dossier(self, person_id):
            for row in self.directory_rows():
                if row["id"] == person_id:
                    return Dossier(person=Person(id=person_id, display_name=row["name"], organization=row["organization"]))
            raise ValueError("missing")

    @dataclass
    class FakeLoops:
        def list(self):
            return []

    @dataclass
    class FakeServices:
        people: FakePeople = field(default_factory=FakePeople)
        loops: FakeLoops = field(default_factory=FakeLoops)

    return FakeServices()
