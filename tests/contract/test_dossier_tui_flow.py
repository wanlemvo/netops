from __future__ import annotations

from netops.domain.models import Dossier, Person, SuggestedAction
from netops.services.people import EditableField
from netops.tui.screens import (
    dossier_screen,
    edit_field_form_screen,
    edit_profile_list_screen,
    log_interaction_form_screen,
    people_list_screen,
    raw_note_form_screen,
)
from netops.tui.state import EditFieldDraft, InteractionDraft, ItemKind, RawNoteDraft, ScreenName


def test_dossier_screen_shows_required_sections_for_minimal_person():
    screen = dossier_screen(Dossier(person=Person(display_name="Avery Chen")))
    text = "\n".join(screen.body)
    for section in ["[Identity]", "[Relationship]", "[Personal Intelligence]", "[Interaction]", "[Opportunity]", "[Raw Notes]"]:
        assert section in text
    assert "Name: Avery Chen" in text
    assert "Role: unset" in text


def test_people_list_headers_are_non_activating():
    screen = people_list_screen(
        [
            {"kind": "header", "name": "A", "id": "", "organization": "", "tags": "", "last_interaction": "", "open_loops": ""},
            {"kind": "person", "id": "p1", "name": "Avery Chen", "organization": "", "tags": "", "last_interaction": "", "open_loops": "0"},
        ]
    )
    assert screen.items[0].label == "A"
    assert screen.items[0].kind == ItemKind.NOOP
    assert screen.items[0].enabled is False
    assert screen.items[1].target == "p1"


def test_log_interaction_form_preserves_validation_message():
    draft = InteractionDraft(person_id="p1", notes="", validation_message="Notes are required.")
    screen = log_interaction_form_screen(draft)
    assert screen.name == ScreenName.LOG_INTERACTION_FORM
    assert any("Notes are required" in line for line in screen.body)


def test_dossier_opportunity_section_shows_suggestions():
    screen = dossier_screen(
        Dossier(
            person=Person(display_name="Avery Chen"),
            suggestions=[
                SuggestedAction(
                    person_id="p1",
                    action_text="Follow up with Avery Chen",
                    reason="open loop",
                    priority_score=60,
                )
            ],
        )
    )
    assert "Suggestion: Follow up with Avery Chen" in "\n".join(screen.body)


def test_edit_profile_list_opens_single_field_edit():
    screen = edit_profile_list_screen(
        "p1",
        [EditableField("role", "Role", "Identity", "text", "Founder")],
    )
    assert screen.name == ScreenName.EDIT_PROFILE_LIST
    assert screen.items[0].target == "edit_field"
    assert screen.items[0].payload["field_key"] == "role"


def test_edit_field_form_preserves_invalid_draft_message():
    screen = edit_field_form_screen(
        EditFieldDraft(
            person_id="p1",
            field_key="relationship_strength",
            label="Relationship Strength",
            value="excellent",
            validation_message="Relationship strength must be 1-5, low, medium, or high.",
        )
    )
    assert screen.name == ScreenName.EDIT_FIELD_FORM
    assert "excellent" in "\n".join(screen.body)
    assert "Relationship strength" in "\n".join(screen.body)


def test_raw_note_form_preserves_validation_message():
    screen = raw_note_form_screen(RawNoteDraft(person_id="p1", validation_message="Note is required."))
    assert screen.name == ScreenName.RAW_NOTE_FORM
    assert any("Note is required" in line for line in screen.body)
