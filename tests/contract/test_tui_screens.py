from __future__ import annotations

from netops.domain.models import DashboardSummary, Dossier, Person
from netops.tui.screens import add_person_form_screen, dossier_screen, overview_screen, people_list_screen
from netops.tui.state import ItemKind, PersonFormDraft, ScreenName, TuiState


def test_people_list_empty_state_has_no_people_and_add_person():
    screen = people_list_screen([])
    assert screen.name == ScreenName.PEOPLE_LIST
    assert screen.items[0].label == "no people"
    assert screen.items[0].enabled is False
    assert screen.items[1].label == "+ Add Person"
    assert screen.items[1].enabled is True


def test_enter_on_no_people_does_nothing(fake_tui_services):
    state = TuiState(fake_tui_services)
    state.open_screen(ScreenName.PEOPLE_LIST)
    state.current.selected_index = 0
    result = state.activate()
    assert result.message == "noop"
    assert state.current.name == ScreenName.PEOPLE_LIST


def test_people_list_person_opens_dossier(fake_tui_services):
    fake_tui_services.people.rows.append(
        {"id": "p1", "name": "Avery Chen", "organization": "Northwind", "tags": "mentor", "last_interaction": "", "open_loops": "0"}
    )
    state = TuiState(fake_tui_services)
    state.open_screen(ScreenName.PEOPLE_LIST)
    result = state.activate()
    assert result.screen.name == ScreenName.DOSSIER


def test_dossier_screen_renders_person_context():
    screen = dossier_screen(Dossier(person=Person(display_name="Avery Chen")))
    assert screen.name == ScreenName.DOSSIER
    assert any("Avery Chen" in line for line in screen.body)


def test_add_person_form_preserves_validation_message():
    draft = PersonFormDraft(organization="Northwind", validation_message="Name is required.")
    screen = add_person_form_screen(draft)
    assert any("Northwind" in line for line in screen.body)
    assert any("Name is required" in line for line in screen.body)


def test_overview_screen_content_and_escape_return(fake_tui_services):
    screen = overview_screen(DashboardSummary(total_people=2, open_loops=1))
    assert any("People: 2" in line for line in screen.body)
    state = TuiState(fake_tui_services)
    state.push(screen)
    state.escape()
    assert state.current.name == ScreenName.MAIN_MENU

