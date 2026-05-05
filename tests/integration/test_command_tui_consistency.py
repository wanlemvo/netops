from __future__ import annotations

from netops.cli import app
from netops.tui.app import NetOpsTui
from netops.tui.state import ScreenName


def test_dashboard_directory_dossier_and_timeline_use_same_records(runner, isolated_db):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen", "--organization", "Northwind"])
    runner.invoke(app, ["log", "Avery Chen", "--type", "meeting", "--notes", "Discussed migration"])

    tui = NetOpsTui()
    assert tui.services.people.dashboard().total_people == 1
    assert tui.services.people.directory_rows()[0]["name"] == "Avery Chen"
    tui.state.move_down()
    tui.state.activate()
    assert tui.state.current.name == ScreenName.PEOPLE_LIST
    tui.state.activate()
    assert tui.state.current.name == ScreenName.DOSSIER
    assert "Avery Chen" in "\n".join(tui.state.current.body)


def test_evaluation_is_visible_in_dossier(runner, isolated_db):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen"])
    runner.invoke(app, ["evaluate", "--person", "Avery Chen", "--outcome", "positive"])
    tui = NetOpsTui()
    tui.state.move_down()
    tui.state.activate()
    tui.state.activate()
    assert "Evaluations: 1" in "\n".join(tui.state.current.body)
