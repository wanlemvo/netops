from __future__ import annotations

from netops.cli import app


def test_quickstart_cli_sequence(runner, isolated_db):
    commands = [
        ["people", "add", "--name", "Avery Chen", "--organization", "Northwind", "--tag", "mentor"],
        ["relationship", "add", "Avery Chen", "--type", "mentor", "--notes", "Quarterly career conversations"],
        [
            "log",
            "Avery Chen",
            "--type",
            "meeting",
            "--notes",
            "Discussed platform migration and promised to send notes",
            "--follow-up",
            "Send migration notes",
        ],
        ["suggest"],
        ["evaluate", "--person", "Avery Chen", "--outcome", "positive", "--notes", "Follow-up strengthened trust"],
    ]
    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.output
