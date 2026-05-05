from __future__ import annotations

import json

from netops.cli import app


def test_people_add_and_list_contract(runner):
    result = runner.invoke(app, ["people", "add", "--name", "Avery Chen", "--organization", "Northwind", "--tag", "mentor"])
    assert result.exit_code == 0, result.output
    assert "Created person" in result.output

    result = runner.invoke(app, ["people", "list"])
    assert result.exit_code == 0, result.output
    assert "Avery Chen" in result.output


def test_relationship_add_and_log_contract(runner):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen"])
    result = runner.invoke(app, ["relationship", "add", "Avery Chen", "--type", "mentor", "--notes", "Career chats"])
    assert result.exit_code == 0, result.output
    assert "Saved relationship" in result.output

    result = runner.invoke(
        app,
        [
            "log",
            "Avery Chen",
            "--type",
            "meeting",
            "--notes",
            "Discussed platform migration",
            "--follow-up",
            "Send notes",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Saved interaction" in result.output
    assert "Created open loop" in result.output


def test_suggest_json_contract(runner):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen"])
    runner.invoke(app, ["log", "Avery Chen", "--type", "meeting", "--notes", "Promised notes", "--follow-up", "Send notes"])
    result = runner.invoke(app, ["suggest", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload[0]["action_text"].startswith("Follow up")


def test_evaluate_contract(runner):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen"])
    result = runner.invoke(app, ["evaluate", "--person", "Avery Chen", "--outcome", "positive"])
    assert result.exit_code == 0, result.output
    assert "Saved evaluation" in result.output

def test_unknown_person_reports_actionable_error(runner):
    result = runner.invoke(app, ["log", "Missing", "--type", "note", "--notes", "Hello"])
    assert result.exit_code == 1
    assert "Add them first" in result.output


def test_direct_commands_still_work_without_textual_dependency(runner):
    add = runner.invoke(app, ["people", "add", "--name", "Nova Reyes"])
    assert add.exit_code == 0, add.output
    listing = runner.invoke(app, ["people", "list"])
    assert listing.exit_code == 0, listing.output
    assert "Nova Reyes" in listing.output
