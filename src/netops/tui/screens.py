from __future__ import annotations

from collections.abc import Sequence

from netops.domain.models import DashboardSummary, Dossier, OpenLoop
from netops.tui.dossier import dossier_actions, dossier_body
from netops.tui.state import ItemKind, ScreenName, ScreenState, SelectableItem


def main_menu_screen() -> ScreenState:
    return ScreenState(
        name=ScreenName.MAIN_MENU,
        title="Main Menu",
        items=[
            SelectableItem("Overview", ItemKind.OPEN_SCREEN, target=ScreenName.OVERVIEW.value, hint="relationship ops dashboard"),
            SelectableItem("People", ItemKind.OPEN_SCREEN, target=ScreenName.PEOPLE_LIST.value, hint="browse dossiers and add people"),
            SelectableItem("Open Loops", ItemKind.OPEN_SCREEN, target=ScreenName.OPEN_LOOPS.value, hint="follow-ups and unresolved threads"),
            SelectableItem("Exit", ItemKind.OPEN_SCREEN, target=ScreenName.EXIT_CONFIRM.value, hint="close NetOps"),
        ],
        status="Select a module. No commands required.",
    )


def exit_confirm_screen() -> ScreenState:
    return ScreenState(
        name=ScreenName.EXIT_CONFIRM,
        title="Exit NetOps?",
        body=["Are you sure you want to exit?"],
        items=[
            SelectableItem("Yes, exit", ItemKind.CONFIRM_EXIT, target="yes"),
            SelectableItem("No, return", ItemKind.CONFIRM_EXIT, target="no"),
        ],
        status="Enter confirms. Escape returns to Main Menu.",
    )


def people_list_screen(rows: list[dict[str, str]]) -> ScreenState:
    items: list[SelectableItem] = []
    if not rows:
        items.append(SelectableItem("no people", ItemKind.NOOP, enabled=False, hint="empty list"))
    for row in rows:
        if row.get("kind") == "header":
            items.append(SelectableItem(row["name"], ItemKind.NOOP, enabled=False, hint="group"))
            continue
        label = row["name"]
        context = " | ".join(part for part in [row.get("organization", ""), row.get("tags", "")] if part)
        if context:
            label = f"{label}  [{context}]"
        items.append(
            SelectableItem(
                label,
                ItemKind.OPEN_DOSSIER,
                target=row["id"],
                hint=f"last: {row.get('last_interaction') or 'never'}  open: {row.get('open_loops') or '0'}",
            )
        )
    items.append(SelectableItem("+ Add Person", ItemKind.OPEN_FORM, hint="create a local person record"))
    selected_index = next((index for index, item in enumerate(items) if item.enabled), 0)
    return ScreenState(
        name=ScreenName.PEOPLE_LIST,
        title="People List",
        items=items,
        selected_index=selected_index,
        status="Enter opens dossier or form. Escape returns to Main Menu.",
    )


def dossier_screen(dossier: Dossier) -> ScreenState:
    person = dossier.person
    return ScreenState(
        name=ScreenName.DOSSIER,
        title=f"Dossier // {person.display_name}",
        body=dossier_body(dossier),
        items=dossier_actions(person.id),
        payload={"person_id": person.id},
        status="Enter selects a dossier action. Escape returns to People List.",
    )


def add_person_form_screen(draft) -> ScreenState:
    fields = [
        ("name", "Name", draft.name),
        ("organization", "Organization", draft.organization),
        ("tags", "Tags", draft.tags),
        ("notes", "Notes", draft.notes),
    ]
    body = []
    for field_name, label, value in fields:
        marker = ">" if draft.active_field == field_name else " "
        body.append(f"{marker} {label}: {value}")
    if draft.validation_message:
        body.append("")
        body.append(f"! {draft.validation_message}")
    return ScreenState(
        name=ScreenName.ADD_PERSON_FORM,
        title="Add Person",
        body=body,
        items=[
            SelectableItem("Save", ItemKind.SAVE_FORM, hint="create person"),
            SelectableItem("Cancel", ItemKind.CANCEL, hint="return to People List"),
        ],
        status="Type to edit active field. Tab changes field. Enter activates Save/Cancel.",
    )


def log_interaction_form_screen(draft) -> ScreenState:
    fields = [
        ("occurred_on", "Date", draft.occurred_on),
        ("interaction_type", "Type", draft.interaction_type),
        ("notes", "Notes", draft.notes),
        ("follow_up", "Follow-up", draft.follow_up),
    ]
    body = []
    for field_name, label, value in fields:
        marker = ">" if draft.active_field == field_name else " "
        body.append(f"{marker} {label}: {value}")
    if draft.validation_message:
        body.append("")
        body.append(f"! {draft.validation_message}")
    return ScreenState(
        name=ScreenName.LOG_INTERACTION_FORM,
        title="Log Interaction",
        body=body,
        items=[
            SelectableItem("Save", ItemKind.SAVE_FORM, hint="log interaction"),
            SelectableItem("Cancel", ItemKind.CANCEL, hint="return to dossier"),
        ],
        payload={"person_id": draft.person_id},
        status="Type to edit active field. Tab changes field. Enter activates Save/Cancel.",
    )


def edit_profile_list_screen(person_id: str, fields) -> ScreenState:
    items = [
        SelectableItem(
            field.label,
            ItemKind.OPEN_FORM,
            target="edit_field",
            hint=f"{field.section}: {field.current_value or 'unset'}",
            payload={"person_id": person_id, "field_key": field.key, "current_value": field.current_value},
        )
        for field in fields
    ]
    items.append(SelectableItem("Back", ItemKind.CANCEL, hint="return to dossier"))
    return ScreenState(
        name=ScreenName.EDIT_PROFILE_LIST,
        title="Edit Profile",
        items=items,
        payload={"person_id": person_id},
        status="Select one field to edit. Escape returns to dossier.",
    )


def edit_field_form_screen(draft) -> ScreenState:
    body = [f"Field: {draft.label}", f"> Value: {draft.value}"]
    if draft.validation_message:
        body.extend(["", f"! {draft.validation_message}"])
    return ScreenState(
        name=ScreenName.EDIT_FIELD_FORM,
        title="Edit Field",
        body=body,
        items=[
            SelectableItem("Save", ItemKind.SAVE_FORM, hint="update field"),
            SelectableItem("Cancel", ItemKind.CANCEL, hint="return to fields"),
        ],
        payload={"person_id": draft.person_id, "field_key": draft.field_key},
        status="Type to edit value. Empty input clears optional fields.",
    )


def raw_note_form_screen(draft) -> ScreenState:
    body = [f"> Note: {draft.note}"]
    if draft.validation_message:
        body.extend(["", f"! {draft.validation_message}"])
    return ScreenState(
        name=ScreenName.RAW_NOTE_FORM,
        title="Append Raw Note",
        body=body,
        items=[
            SelectableItem("Save", ItemKind.SAVE_FORM, hint="append note"),
            SelectableItem("Cancel", ItemKind.CANCEL, hint="return to dossier"),
        ],
        payload={"person_id": draft.person_id},
        status="Saving appends a new raw note and preserves previous notes.",
    )


def overview_screen(summary: DashboardSummary) -> ScreenState:
    body = [
        f"People: {summary.total_people}",
        f"Recent interactions: {summary.recent_interactions}",
        f"Open loops: {summary.open_loops}",
        f"Overdue follow-ups: {summary.overdue_followups}",
        f"Due soon: {summary.due_soon_followups}",
    ]
    if summary.top_suggestions:
        body.append("")
        body.append("[Top Follow-Ups]")
        body.extend(f"- {suggestion.action_text}" for suggestion in summary.top_suggestions[:3])
    return ScreenState(
        name=ScreenName.OVERVIEW,
        title="Overview",
        body=body,
        items=[SelectableItem("Back", ItemKind.CANCEL)],
        status="Escape returns to Main Menu.",
    )


def open_loops_screen(loops: Sequence[OpenLoop]) -> ScreenState:
    items: list[SelectableItem] = []
    if not loops:
        items.append(SelectableItem("no open loops", ItemKind.NOOP, enabled=False))
    for loop in loops:
        due = f" due {loop.due_on}" if loop.due_on else ""
        items.append(SelectableItem(f"{loop.description} [{loop.status.value}{due}]", ItemKind.NOOP, enabled=False))
    return ScreenState(
        name=ScreenName.OPEN_LOOPS,
        title="Open Loops",
        items=items,
        status="Open-loop editing stays in direct commands for now. Escape returns to Main Menu.",
    )


def error_screen(message: str) -> ScreenState:
    return ScreenState(
        name=ScreenName.ERROR,
        title="Recoverable Error",
        body=[message],
        items=[
            SelectableItem("Return to Main Menu", ItemKind.OPEN_SCREEN, target=ScreenName.MAIN_MENU.value),
            SelectableItem("Exit", ItemKind.OPEN_SCREEN, target=ScreenName.EXIT_CONFIRM.value),
        ],
        status="Choose a recovery action.",
    )


def visible_rows(screen: ScreenState, *, height: int) -> list[SelectableItem]:
    if height <= 0 or len(screen.items) <= height:
        return screen.items
    screen.clamp_selection()
    start = max(0, min(screen.selected_index, len(screen.items) - height))
    return screen.items[start : start + height]


def has_clipped_rows(screen: ScreenState, *, height: int) -> bool:
    return height > 0 and len(screen.items) > height
