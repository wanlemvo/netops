from __future__ import annotations

from netops.services import EvaluationService, InteractionService, OpenLoopService, PeopleService, SuggestionService
from netops.storage import NetOpsRepository, connect
from netops.tui.app import NetOpsTuiServices
from netops.tui.state import ScreenName, TuiState


def make_services(db_path):
    repository = NetOpsRepository(connect(db_path))
    people = PeopleService(repository)
    interactions = InteractionService(repository, people)
    loops = OpenLoopService(repository, people)
    suggestions = SuggestionService(repository, people)
    evaluations = EvaluationService(repository, people)
    return NetOpsTuiServices(repository, people, interactions, loops, suggestions, evaluations)


def test_selecting_people_from_main_menu_opens_list_and_dossier(isolated_db):
    services = make_services(isolated_db)
    person = services.people.create_person(name="Avery Chen", organization="Northwind")
    state = TuiState(services)
    state.move_down()
    assert state.current.selected_item.label == "People"
    state.activate()
    assert state.current.name == ScreenName.PEOPLE_LIST
    assert state.current.selected_item.target == person.id
    state.activate()
    assert state.current.name == ScreenName.DOSSIER
    state.escape()
    assert state.current.name == ScreenName.PEOPLE_LIST


def test_add_person_form_saves_and_refreshes_people_list(isolated_db):
    services = make_services(isolated_db)
    state = TuiState(services)
    state.open_screen(ScreenName.PEOPLE_LIST)
    assert state.current.selected_item.label == "+ Add Person"
    state.activate()
    assert state.current.name == ScreenName.ADD_PERSON_FORM
    state.form_draft.name = "Nova Reyes"
    state.form_draft.organization = "Afterlight"
    state.save_person_form()
    assert state.current.name == ScreenName.PEOPLE_LIST
    assert any("Nova Reyes" in item.label for item in state.current.items)

