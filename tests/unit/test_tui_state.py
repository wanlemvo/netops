from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from netops.domain.models import DashboardSummary, Dossier, Person
from netops.tui.screens import has_clipped_rows, main_menu_screen, visible_rows
from netops.tui.state import ItemKind, PersonFormDraft, ScreenName, ScreenState, SelectableItem, TuiState


@dataclass
class FakePeople:
    rows: list[dict[str, str]] = field(default_factory=list)
    created: list[Person] = field(default_factory=list)

    def directory_rows(self):
        return self.rows + [
            {
                "id": person.id,
                "name": person.display_name,
                "organization": person.organization or "",
                "tags": ", ".join(person.tags),
                "last_interaction": "",
                "open_loops": "0",
            }
            for person in self.created
        ]

    def dashboard(self):
        return DashboardSummary(total_people=len(self.directory_rows()))

    def create_person(self, *, name, organization=None, tags=None, notes=None, **_):
        person = Person(display_name=name, organization=organization, tags=tags or [], relationship_notes=notes)
        self.created.append(person)
        return person

    @property
    def repository(self):
        return self

    def dossier(self, person_id):
        for row in self.directory_rows():
            if row["id"] == person_id:
                return Dossier(person=Person(id=person_id, display_name=row["name"], organization=row["organization"]))
        raise ValueError("missing")


@dataclass
class FakeLoops:
    def list(self):
        return []


@dataclass
class FakeServices:
    people: FakePeople = field(default_factory=FakePeople)
    loops: FakeLoops = field(default_factory=FakeLoops)


@pytest.fixture()
def fake_tui_services():
    return FakeServices()


def test_main_menu_options():
    screen = main_menu_screen()
    assert [item.label for item in screen.items] == ["Overview", "People", "Open Loops", "Exit"]


def test_selection_movement_and_bounds(fake_tui_services):
    state = TuiState(fake_tui_services)
    state.move_up()
    assert state.current.selected_index == 0
    state.move_down()
    state.move_down()
    assert state.current.selected_item.label == "Open Loops"


def test_disabled_item_activation_is_noop(fake_tui_services):
    state = TuiState(fake_tui_services)
    state.current = ScreenState(
        name=ScreenName.PEOPLE_LIST,
        title="People",
        items=[SelectableItem("no people", ItemKind.NOOP, enabled=False)],
    )
    result = state.activate()
    assert result.message == "noop"
    assert state.current.name == ScreenName.PEOPLE_LIST


def test_escape_on_main_menu_shows_exit_confirmation(fake_tui_services):
    state = TuiState(fake_tui_services)
    state.escape()
    assert state.current.name == ScreenName.EXIT_CONFIRM
    assert [item.label for item in state.current.items] == ["Yes, exit", "No, return"]


def test_person_form_draft_preserves_values_on_validation_failure():
    draft = PersonFormDraft(organization="Northwind", tags="mentor", notes="Quarterly")
    assert draft.validate() is False
    assert draft.organization == "Northwind"
    assert draft.tags == "mentor"
    assert draft.validation_message == "Name is required."


def test_save_person_form_refreshes_people_list(fake_tui_services):
    state = TuiState(fake_tui_services)
    state.open_screen(ScreenName.PEOPLE_LIST)
    state.activate()
    state.form_draft.name = "Avery Chen"
    state.form_draft.organization = "Northwind"
    state.save_person_form()
    assert state.current.name == ScreenName.PEOPLE_LIST
    assert any("Avery Chen" in item.label for item in state.current.items)


def test_visible_rows_indicate_clipping():
    screen = ScreenState(
        name=ScreenName.MAIN_MENU,
        title="Long",
        items=[SelectableItem(str(i), ItemKind.NOOP) for i in range(20)],
        selected_index=10,
    )
    assert len(visible_rows(screen, height=5)) == 5
    assert has_clipped_rows(screen, height=5) is True

