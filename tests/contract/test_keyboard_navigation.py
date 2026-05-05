from __future__ import annotations

from pathlib import Path

from netops.tui.app import NetOpsTui
from netops.tui.state import ScreenName, TuiState


def test_no_textual_dependency_or_imports():
    pyproject = Path("pyproject.toml").read_text()
    app_source = Path("src/netops/tui/app.py").read_text()
    assert "textual" not in pyproject.lower()
    assert "textual" not in app_source.lower()


def test_keyboard_bindings_are_registered(isolated_db):
    tui = NetOpsTui()
    source = Path("src/netops/tui/app.py").read_text()
    for key in ['"up"', '"down"', '"enter"', '"escape"']:
        assert f"@bindings.add({key})" in source
    assert "mouse_support=False" in source
    assert tui.render_text_for_tests()


def test_up_down_enter_escape_navigation(fake_tui_services):
    state = TuiState(fake_tui_services)
    assert state.current.name == ScreenName.MAIN_MENU
    state.move_down()
    assert state.current.selected_item.label == "People"
    result = state.activate()
    assert result.screen.name == ScreenName.PEOPLE_LIST
    state.escape()
    assert state.current.name == ScreenName.MAIN_MENU
    state.escape()
    assert state.current.name == ScreenName.EXIT_CONFIRM
