from __future__ import annotations

import json

from netops.cli import app


def test_cli_review_v1_lists_person_and_opportunity_follow_ups(runner):
    runner.invoke(
        app,
        [
            "people",
            "add",
            "--name",
            "Harper Vale",
            "--next-action",
            "Schedule mock interview.",
            "--follow-up-date",
            "2026-06-15",
        ],
    )
    runner.invoke(
        app,
        [
            "opportunity",
            "add",
            "--person",
            "Harper Vale",
            "--title",
            "Portfolio Review",
            "--follow-up-date",
            "2026-06-14",
        ],
    )

    result = runner.invoke(app, ["loops", "review-v1", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)

    assert [row["kind"] for row in payload] == ["opportunity", "person"]
    assert payload[0]["title"] == "Portfolio Review"
    assert payload[1]["action"] == "Schedule mock interview."


def test_v1_opportunities_do_not_generate_rule_based_suggestions(runner):
    runner.invoke(app, ["people", "add", "--name", "Harper Vale"])
    runner.invoke(app, ["opportunity", "add", "--person", "Harper Vale", "--title", "Mock Interview"])

    result = runner.invoke(app, ["suggest", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == []
