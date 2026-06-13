from __future__ import annotations

import json

from netops.cli import app


def test_cli_multi_person_opportunity_and_relationship_link_flow(runner):
    runner.invoke(app, ["people", "add", "--name", "Henry Valentine"])
    runner.invoke(app, ["people", "add", "--name", "Benjamin Chan"])

    opportunity = runner.invoke(
        app,
        [
            "opportunity",
            "add",
            "--person",
            "Henry Valentine",
            "--person",
            "Benjamin Chan",
            "--title",
            "Mock Interview",
            "--description",
            "Practice interview with cybersecurity leaders.",
            "--follow-up-date",
            "2026-06-15",
        ],
    )
    assert opportunity.exit_code == 0, opportunity.output

    henry_opps = runner.invoke(app, ["opportunity", "list", "Henry Valentine", "--json"])
    benjamin_opps = runner.invoke(app, ["opportunity", "list", "Benjamin Chan", "--json"])
    assert json.loads(henry_opps.output)[0]["title"] == "Mock Interview"
    assert json.loads(benjamin_opps.output)[0]["title"] == "Mock Interview"

    link = runner.invoke(
        app,
        ["relationship", "link", "Henry Valentine", "Benjamin Chan", "--type", "works_with", "--description", "T-Mobile network."],
    )
    assert link.exit_code == 0, link.output
    assert "Saved relationship link" in link.output
