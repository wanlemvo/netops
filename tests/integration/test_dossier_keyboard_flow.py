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


def test_keyboard_flow_creates_person_opens_dossier_and_logs_interaction(isolated_db):
    services = make_services(isolated_db)
    state = TuiState(services)
    state.open_screen(ScreenName.PEOPLE_LIST)
    state.activate()
    state.form_draft.name = "Avery Chen"
    state.save_person_form()
    state.activate()
    assert state.current.name == ScreenName.DOSSIER
    assert "[Identity]" in "\n".join(state.current.body)

    state.activate()
    assert state.current.name == ScreenName.LOG_INTERACTION_FORM
    state.interaction_draft.notes = "Met about follow-up system"
    state.interaction_draft.follow_up = "Send prototype"
    state.save_interaction_form()
    text = "\n".join(state.current.body)
    assert "Met about follow-up system" in text
    assert "Suggestion: Follow up with Avery Chen: Send prototype" in text


def test_people_list_is_alphabetized_with_non_activating_headers(isolated_db):
    services = make_services(isolated_db)
    services.people.create_person(name="Beta Contact")
    services.people.create_person(name="Avery Chen")
    services.people.create_person(name="3M Contact")
    state = TuiState(services)
    state.open_screen(ScreenName.PEOPLE_LIST)
    labels = [item.label for item in state.current.items[:5]]
    assert labels == ["#", "3M Contact", "A", "Avery Chen", "B"]
    assert state.current.selected_item.label == "3M Contact"


def test_keyboard_flow_edits_profile_field_and_appends_raw_note(isolated_db):
    services = make_services(isolated_db)
    person = services.people.create_person(name="Avery Chen")
    state = TuiState(services)
    state.open_dossier(person.id)
    state.current.selected_index = 2
    state.activate()
    assert state.current.name == ScreenName.EDIT_PROFILE_LIST
    state.current.selected_index = 3
    state.activate()
    assert state.current.name == ScreenName.EDIT_FIELD_FORM
    state.edit_field_draft.value = "Founder"
    state.save_edit_field_form()
    assert "Role: Founder" in "\n".join(state.current.body)

    state.current.selected_index = 4
    state.activate()
    assert state.current.name == ScreenName.RAW_NOTE_FORM
    state.raw_note_draft.note = "Prefers concise Friday updates"
    state.save_raw_note_form()
    assert "Prefers concise Friday updates" in "\n".join(state.current.body)
