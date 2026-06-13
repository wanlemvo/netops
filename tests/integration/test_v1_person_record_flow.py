from __future__ import annotations

import json

from netops.cli import app


def test_cli_v1_person_create_show_edit_reopen_flow(runner):
    add = runner.invoke(
        app,
        [
            "people",
            "add",
            "--name",
            "Henry Valentine",
            "--organization",
            "T-Mobile",
            "--relationship-strength",
            "Medium-High",
            "--origin-story",
            "Introduced through T-Mobile network.",
            "--dossier",
            "Cybersecurity leader.\nOffered mock interview support.",
            "--next-action",
            "Schedule mock interview.",
            "--follow-up-date",
            "2026-06-15",
            "--tag",
            "cybersecurity",
        ],
    )
    assert add.exit_code == 0, add.output

    shown = runner.invoke(app, ["people", "show", "Henry Valentine", "--json"])
    assert shown.exit_code == 0, shown.output
    payload = json.loads(shown.output)
    assert payload["relationship_strength"] == "Medium-High"
    assert payload["origin_story"] == "Introduced through T-Mobile network."
    assert payload["dossier"] == "Cybersecurity leader.\nOffered mock interview support."

    edit = runner.invoke(
        app,
        ["people", "edit", "Henry Valentine", "--field", "next_action", "--value", "Send portfolio."],
    )
    assert edit.exit_code == 0, edit.output

    reopened = runner.invoke(app, ["people", "show", "Henry Valentine", "--json"])
    assert reopened.exit_code == 0, reopened.output
    assert json.loads(reopened.output)["next_action"] == "Send portfolio."


def test_cli_v1_person_missing_optional_fields_reopen_as_unset(runner):
    add = runner.invoke(app, ["people", "add", "--name", "Dr Olav"])
    assert add.exit_code == 0, add.output

    shown = runner.invoke(app, ["people", "show", "Dr Olav", "--json"])
    assert shown.exit_code == 0, shown.output
    payload = json.loads(shown.output)

    assert payload["name"] == "Dr Olav"
    assert payload["alias"] is None
    assert payload["origin_story"] is None
