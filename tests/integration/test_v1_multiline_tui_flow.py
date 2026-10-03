from __future__ import annotations

from netops.tui.screens import add_person_form_screen, edit_field_form_screen
from netops.tui.state import EditFieldDraft, PersonFormDraft


def test_tui_person_form_draft_accepts_pasted_multiline_text():
    draft = PersonFormDraft(name="Harper Vale", active_field="dossier")
    pasted = "First line\nSecond line\n" + "A" * 2000

    draft.append_text(pasted)

    assert draft.dossier == pasted


def test_tui_screens_render_multiline_fields_as_visible_rows():
    person_draft = PersonFormDraft(name="Harper Vale", dossier="First line\nSecond line")
    person_draft.active_field = "dossier"
    person_screen = add_person_form_screen(person_draft)

    edit_screen = edit_field_form_screen(
        EditFieldDraft(field_key="dossier", label="Dossier", value="Alpha\nBeta")
    )

    assert "> Dossier: First line" in person_screen.body
    assert "           Second line" in person_screen.body
    assert "> Value: Alpha" in edit_screen.body
    assert "         Beta" in edit_screen.body
