from __future__ import annotations

from netops.cli import app
from netops.storage import NetOpsRepository, connect


def test_capture_workflow_persists_person_relationship_interaction_and_loop(runner, isolated_db):
    assert runner.invoke(app, ["people", "add", "--name", "Avery Chen", "--organization", "Northwind"]).exit_code == 0
    assert runner.invoke(app, ["relationship", "add", "Avery Chen", "--type", "mentor"]).exit_code == 0
    assert (
        runner.invoke(
            app,
            ["log", "Avery Chen", "--type", "meeting", "--notes", "Promised notes", "--follow-up", "Send notes"],
        ).exit_code
        == 0
    )

    repository = NetOpsRepository(connect(isolated_db))
    person = repository.list_people()[0]
    assert repository.list_relationships(person.id)
    assert repository.list_interactions(person.id)
    assert repository.list_open_loops(person.id)


def test_storage_recovery_creates_missing_database(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    assert repository.list_people() == []

