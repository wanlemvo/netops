from __future__ import annotations

from collections.abc import Sequence

from netops.domain.models import DashboardSummary, Dossier, OpenLoop
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
    selected_index = 0 if rows else 1
    return ScreenState(
        name=ScreenName.PEOPLE_LIST,
        title="People List",
        items=items,
        selected_index=selected_index,
        status="Enter opens dossier or form. Escape returns to Main Menu.",
    )


def dossier_screen(dossier: Dossier) -> ScreenState:
    person = dossier.person
    body = [
        f"Name: {person.display_name}",
        f"Organization: {person.organization or 'None'}",
        f"Tags: {', '.join(person.tags) or 'None'}",
        f"Relationship notes: {person.relationship_notes or 'None'}",
        "",
        f"Open loops: {len(dossier.open_loops)}",
        f"Recent interactions: {len(dossier.recent_interactions)}",
        f"Suggestions: {len(dossier.suggestions)}",
        f"Evaluations: {len(dossier.evaluations)}",
    ]
    return ScreenState(
        name=ScreenName.DOSSIER,
        title=f"Dossier // {person.display_name}",
        body=body,
        items=[SelectableItem("Back", ItemKind.CANCEL, hint="return to People List")],
        payload={"person_id": person.id},
        status="Escape returns to People List.",
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


def overview_screen(summary: DashboardSummary) -> ScreenState:
    body = [
        f"People: {summary.total_people}",
        f"Recent interactions: {summary.recent_interactions}",
        f"Open loops: {summary.open_loops}",
        f"Overdue follow-ups: {summary.overdue_followups}",
        f"Due soon: {summary.due_soon_followups}",
    ]
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
