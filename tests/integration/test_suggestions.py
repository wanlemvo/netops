from __future__ import annotations

from datetime import date, timedelta

from netops.cli import app


def test_suggestion_scenarios_for_overdue_stale_and_empty(runner, isolated_db):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen"])
    runner.invoke(
        app,
        [
            "log",
            "Avery Chen",
            "--type",
            "meeting",
            "--notes",
            "Promised notes",
            "--follow-up",
            "Send notes",
            "--due",
            (date.today() - timedelta(days=1)).isoformat(),
        ],
    )
    result = runner.invoke(app, ["suggest"])
    assert result.exit_code == 0, result.output
    assert "overdue" in result.output


def test_no_people_has_clear_empty_suggestion_message(runner, isolated_db):
    result = runner.invoke(app, ["suggest"])
    assert result.exit_code == 0
    assert "No useful suggestions" in result.output

