from __future__ import annotations

import json

from netops.cli import app


def test_cli_contact_methods_add_list_set_primary_delete(runner):
    add_person = runner.invoke(app, ["people", "add", "--name", "Harper Vale"])
    assert add_person.exit_code == 0, add_person.output

    email = runner.invoke(
        app,
        ["people", "contact", "add", "Harper Vale", "--type", "email", "--label", "work", "--value", "henry@example.com"],
    )
    assert email.exit_code == 0, email.output

    phone = runner.invoke(
        app,
        ["people", "contact", "add", "Harper Vale", "--type", "phone", "--label", "mobile", "--value", "555-0100", "--primary"],
    )
    assert phone.exit_code == 0, phone.output

    listed = runner.invoke(app, ["people", "contact", "list", "Harper Vale", "--json"])
    assert listed.exit_code == 0, listed.output
    payload = json.loads(listed.output)
    assert {item["type"] for item in payload} == {"email", "phone"}
    phone_id = next(item["contact_method_id"] for item in payload if item["type"] == "phone")

    primary = runner.invoke(app, ["people", "contact", "set-primary", phone_id])
    assert primary.exit_code == 0, primary.output

    deleted = runner.invoke(app, ["people", "contact", "delete", phone_id])
    assert deleted.exit_code == 0, deleted.output

    relisted = runner.invoke(app, ["people", "contact", "list", "Harper Vale", "--json"])
    assert relisted.exit_code == 0, relisted.output
    assert [item["type"] for item in json.loads(relisted.output)] == ["email"]
