from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class ScreenName(StrEnum):
    MAIN_MENU = "main_menu"
    OVERVIEW = "overview"
    PEOPLE_LIST = "people_list"
    DOSSIER = "dossier"
    ADD_PERSON_FORM = "add_person_form"
    OPEN_LOOPS = "open_loops"
    ERROR = "error"
    EXIT_CONFIRM = "exit_confirm"


class ItemKind(StrEnum):
    OPEN_SCREEN = "open_screen"
    OPEN_DOSSIER = "open_dossier"
    OPEN_FORM = "open_form"
    SAVE_FORM = "save_form"
    CONFIRM_EXIT = "confirm_exit"
    CANCEL = "cancel"
    NOOP = "noop"


@dataclass(slots=True)
class SelectableItem:
    label: str
    kind: ItemKind | str
    enabled: bool = True
    target: str | None = None
    hint: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScreenState:
    name: ScreenName
    title: str
    items: list[SelectableItem] = field(default_factory=list)
    selected_index: int = 0
    payload: dict[str, Any] = field(default_factory=dict)
    body: list[str] = field(default_factory=list)
    status: str = ""

    def clamp_selection(self) -> None:
        if not self.items:
            self.selected_index = 0
            return
        self.selected_index = max(0, min(self.selected_index, len(self.items) - 1))

    @property
    def selected_item(self) -> SelectableItem | None:
        if not self.items:
            return None
        self.clamp_selection()
        return self.items[self.selected_index]


@dataclass(slots=True)
class NavigationResult:
    screen: ScreenState
    exit_requested: bool = False
    message: str = ""


@dataclass(slots=True)
class PersonFormDraft:
    name: str = ""
    organization: str = ""
    tags: str = ""
    notes: str = ""
    active_field: str = "name"
    validation_message: str = ""

    fields: tuple[str, ...] = ("name", "organization", "tags", "notes")

    def has_values(self) -> bool:
        return any(getattr(self, field_name).strip() for field_name in self.fields)

    def validate(self) -> bool:
        if not self.name.strip():
            self.validation_message = "Name is required."
            self.active_field = "name"
            return False
        self.validation_message = ""
        return True

    def tags_list(self) -> list[str]:
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def append_text(self, text: str) -> None:
        current = getattr(self, self.active_field)
        setattr(self, self.active_field, current + text)

    def backspace(self) -> None:
        current = getattr(self, self.active_field)
        setattr(self, self.active_field, current[:-1])

    def next_field(self) -> None:
        index = self.fields.index(self.active_field)
        self.active_field = self.fields[(index + 1) % len(self.fields)]

    def previous_field(self) -> None:
        index = self.fields.index(self.active_field)
        self.active_field = self.fields[(index - 1) % len(self.fields)]


class TuiServices(Protocol):
    people: Any
    loops: Any


class TuiState:
    def __init__(self, services: TuiServices) -> None:
        self.services = services
        self.stack: list[ScreenState] = []
        self.exit_requested = False
        self.form_draft = PersonFormDraft()
        self.current = self.build_main_menu()

    def build_main_menu(self) -> ScreenState:
        from netops.tui.screens import main_menu_screen

        return main_menu_screen()

    def push(self, screen: ScreenState) -> ScreenState:
        self.stack.append(self.current)
        self.current = screen
        self.current.clamp_selection()
        return self.current

    def pop(self) -> ScreenState:
        if self.stack:
            self.current = self.stack.pop()
        return self.current

    def move_up(self) -> ScreenState:
        if self.current.items:
            self.current.selected_index = max(0, self.current.selected_index - 1)
        return self.current

    def move_down(self) -> ScreenState:
        if self.current.items:
            self.current.selected_index = min(len(self.current.items) - 1, self.current.selected_index + 1)
        return self.current

    def enter_text(self, text: str) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM and text:
            self.form_draft.append_text(text)
            self.refresh_current()
        return self.current

    def backspace(self) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM:
            self.form_draft.backspace()
            self.refresh_current()
        return self.current

    def tab_field(self, *, backwards: bool = False) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM:
            if backwards:
                self.form_draft.previous_field()
            else:
                self.form_draft.next_field()
            self.refresh_current()
        return self.current

    def activate(self) -> NavigationResult:
        item = self.current.selected_item
        if item is None or not item.enabled or item.kind == ItemKind.NOOP:
            return NavigationResult(self.current, message="noop")

        if item.kind == ItemKind.OPEN_SCREEN:
            return NavigationResult(self.open_screen(ScreenName(item.target)))
        if item.kind == ItemKind.OPEN_DOSSIER:
            return NavigationResult(self.open_dossier(item.target or ""))
        if item.kind == ItemKind.OPEN_FORM:
            self.form_draft = PersonFormDraft()
            return NavigationResult(self.push(self.build_add_person_form()))
        if item.kind == ItemKind.SAVE_FORM:
            return NavigationResult(self.save_person_form())
        if item.kind == ItemKind.CONFIRM_EXIT:
            if item.target == "yes":
                self.exit_requested = True
                return NavigationResult(self.current, exit_requested=True)
            self.current = self.build_main_menu()
            self.stack.clear()
            return NavigationResult(self.current)
        if item.kind == ItemKind.CANCEL:
            return NavigationResult(self.escape())

        return NavigationResult(self.current, message="noop")

    def escape(self) -> ScreenState:
        if self.current.name == ScreenName.MAIN_MENU:
            self.current = self.build_exit_confirm()
            return self.current
        if self.current.name == ScreenName.EXIT_CONFIRM:
            self.current = self.build_main_menu()
            self.stack.clear()
            return self.current
        if self.current.name == ScreenName.ADD_PERSON_FORM and self.form_draft.has_values():
            self.current.status = "Unsaved draft discarded. Press Escape again from People to go back."
            self.form_draft = PersonFormDraft()
            return self.pop()
        return self.pop()

    def open_screen(self, name: ScreenName) -> ScreenState:
        if name == ScreenName.MAIN_MENU:
            self.stack.clear()
            self.current = self.build_main_menu()
            return self.current
        if name == ScreenName.OVERVIEW:
            return self.push(self.build_overview())
        if name == ScreenName.PEOPLE_LIST:
            return self.push(self.build_people_list())
        if name == ScreenName.OPEN_LOOPS:
            return self.push(self.build_open_loops())
        if name == ScreenName.EXIT_CONFIRM:
            return self.push(self.build_exit_confirm())
        return self.push(self.build_error("Unknown screen."))

    def open_dossier(self, person_id: str) -> ScreenState:
        from netops.tui.screens import dossier_screen

        try:
            dossier = self.services.people.repository.dossier(person_id)
            return self.push(dossier_screen(dossier))
        except Exception as exc:
            return self.push(self.build_error(f"Could not load dossier: {exc}"))

    def save_person_form(self) -> ScreenState:
        if not self.form_draft.validate():
            self.refresh_current()
            return self.current
        self.services.people.create_person(
            name=self.form_draft.name.strip(),
            organization=self.form_draft.organization.strip() or None,
            tags=self.form_draft.tags_list(),
            notes=self.form_draft.notes.strip() or None,
        )
        self.form_draft = PersonFormDraft()
        self.current = self.build_people_list()
        self.stack = [self.build_main_menu()]
        return self.current

    def refresh_current(self) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM:
            self.current = self.build_add_person_form()
        elif self.current.name == ScreenName.PEOPLE_LIST:
            selected = self.current.selected_index
            self.current = self.build_people_list()
            self.current.selected_index = min(selected, max(0, len(self.current.items) - 1))
        return self.current

    def build_people_list(self) -> ScreenState:
        from netops.tui.screens import people_list_screen

        return people_list_screen(self.services.people.directory_rows())

    def build_overview(self) -> ScreenState:
        from netops.tui.screens import overview_screen

        return overview_screen(self.services.people.dashboard())

    def build_open_loops(self) -> ScreenState:
        from netops.tui.screens import open_loops_screen

        return open_loops_screen(self.services.loops.list())

    def build_add_person_form(self) -> ScreenState:
        from netops.tui.screens import add_person_form_screen

        return add_person_form_screen(self.form_draft)

    def build_exit_confirm(self) -> ScreenState:
        from netops.tui.screens import exit_confirm_screen

        return exit_confirm_screen()

    def build_error(self, message: str) -> ScreenState:
        from netops.tui.screens import error_screen

        return error_screen(message)
