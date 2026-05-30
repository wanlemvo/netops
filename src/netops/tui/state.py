from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any, Protocol

from netops.domain.models import OpenLoopStatus, SuggestionStatus


class ScreenName(StrEnum):
    MAIN_MENU = "main_menu"
    OVERVIEW = "overview"
    PEOPLE_LIST = "people_list"
    DOSSIER = "dossier"
    ADD_PERSON_FORM = "add_person_form"
    LOG_INTERACTION_FORM = "log_interaction_form"
    EDIT_PROFILE_LIST = "edit_profile_list"
    EDIT_FIELD_FORM = "edit_field_form"
    RAW_NOTE_FORM = "raw_note_form"
    CONTACT_FORM = "contact_form"
    OPEN_LOOP_FORM = "open_loop_form"
    OPEN_LOOPS = "open_loops"
    LOOP_DETAIL = "loop_detail"
    SUGGESTIONS = "suggestions"
    SUGGESTION_DETAIL = "suggestion_detail"
    DELETE_CONFIRM = "delete_confirm"
    ERROR = "error"
    EXIT_CONFIRM = "exit_confirm"


class ItemKind(StrEnum):
    OPEN_SCREEN = "open_screen"
    OPEN_DOSSIER = "open_dossier"
    OPEN_FORM = "open_form"
    SAVE_FORM = "save_form"
    ACTION = "action"
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
    alias: str = ""
    role: str = ""
    organization: str = ""
    location: str = ""
    birthday: str = ""
    tags: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    other_social: str = ""
    relationship_type: str = ""
    relationship_strength: str = ""
    notes: str = ""
    interests: str = ""
    communication_style: str = ""
    preferences_notes: str = ""
    signals: str = ""
    active_field: str = "name"
    validation_message: str = ""

    fields: tuple[str, ...] = (
        "name",
        "alias",
        "role",
        "organization",
        "location",
        "birthday",
        "tags",
        "email",
        "phone",
        "linkedin",
        "github",
        "other_social",
        "relationship_type",
        "relationship_strength",
        "notes",
        "interests",
        "communication_style",
        "preferences_notes",
        "signals",
    )

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

    def interests_list(self) -> list[str]:
        return [interest.strip() for interest in self.interests.split(",") if interest.strip()]

    def signals_list(self) -> list[str]:
        return [signal.strip() for signal in self.signals.split(",") if signal.strip()]

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


@dataclass(slots=True)
class InteractionDraft:
    person_id: str = ""
    occurred_on: str = field(default_factory=lambda: date.today().isoformat())
    interaction_type: str = "note"
    notes: str = ""
    follow_up: str = ""
    due_on: str = ""
    active_field: str = "notes"
    validation_message: str = ""

    fields: tuple[str, ...] = ("occurred_on", "interaction_type", "notes", "follow_up", "due_on")

    def has_values(self) -> bool:
        return any(getattr(self, field_name).strip() for field_name in self.fields)

    def validate(self) -> bool:
        try:
            date.fromisoformat(self.occurred_on.strip())
        except ValueError:
            self.validation_message = "Date must be YYYY-MM-DD."
            self.active_field = "occurred_on"
            return False
        if not self.interaction_type.strip():
            self.validation_message = "Interaction type is required."
            self.active_field = "interaction_type"
            return False
        if not self.notes.strip():
            self.validation_message = "Notes are required."
            self.active_field = "notes"
            return False
        if self.due_on.strip():
            try:
                date.fromisoformat(self.due_on.strip())
            except ValueError:
                self.validation_message = "Follow-up due date must be YYYY-MM-DD."
                self.active_field = "due_on"
                return False
        self.validation_message = ""
        return True

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


@dataclass(slots=True)
class EditFieldDraft:
    person_id: str = ""
    field_key: str = ""
    label: str = ""
    value: str = ""
    validation_message: str = ""

    def has_values(self) -> bool:
        return bool(self.value.strip())

    def append_text(self, text: str) -> None:
        self.value += text

    def backspace(self) -> None:
        self.value = self.value[:-1]


@dataclass(slots=True)
class RawNoteDraft:
    person_id: str = ""
    note: str = ""
    validation_message: str = ""

    def has_values(self) -> bool:
        return bool(self.note.strip())

    def validate(self) -> bool:
        if not self.note.strip():
            self.validation_message = "Note is required."
            return False
        self.validation_message = ""
        return True

    def append_text(self, text: str) -> None:
        self.note += text

    def backspace(self) -> None:
        self.note = self.note[:-1]


@dataclass(slots=True)
class ContactDraft:
    person_id: str = ""
    kind: str = "email"
    label: str = ""
    value: str = ""
    active_field: str = "value"
    validation_message: str = ""

    fields: tuple[str, ...] = ("kind", "label", "value")

    def has_values(self) -> bool:
        return any(getattr(self, field_name).strip() for field_name in self.fields)

    def validate(self) -> bool:
        if not self.value.strip():
            self.validation_message = "Contact value is required."
            self.active_field = "value"
            return False
        self.validation_message = ""
        return True

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


@dataclass(slots=True)
class OpenLoopDraft:
    person_id: str = ""
    description: str = ""
    due_on: str = ""
    priority: str = ""
    active_field: str = "description"
    validation_message: str = ""

    fields: tuple[str, ...] = ("description", "due_on", "priority")

    def has_values(self) -> bool:
        return any(getattr(self, field_name).strip() for field_name in self.fields)

    def validate(self) -> bool:
        if not self.description.strip():
            self.validation_message = "Follow-up description is required."
            self.active_field = "description"
            return False
        if self.due_on.strip():
            try:
                date.fromisoformat(self.due_on.strip())
            except ValueError:
                self.validation_message = "Due date must be YYYY-MM-DD."
                self.active_field = "due_on"
                return False
        if self.priority.strip():
            try:
                int(self.priority.strip())
            except ValueError:
                self.validation_message = "Priority must be a number."
                self.active_field = "priority"
                return False
        self.validation_message = ""
        return True

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
    interactions: Any
    loops: Any
    suggestions: Any


class TuiState:
    def __init__(self, services: TuiServices) -> None:
        self.services = services
        self.stack: list[ScreenState] = []
        self.exit_requested = False
        self.form_draft = PersonFormDraft()
        self.interaction_draft = InteractionDraft()
        self.edit_field_draft = EditFieldDraft()
        self.raw_note_draft = RawNoteDraft()
        self.contact_draft = ContactDraft()
        self.open_loop_draft = OpenLoopDraft()
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
            for index in range(self.current.selected_index - 1, -1, -1):
                if self.current.items[index].enabled:
                    self.current.selected_index = index
                    break
        return self.current

    def move_down(self) -> ScreenState:
        if self.current.items:
            for index in range(self.current.selected_index + 1, len(self.current.items)):
                if self.current.items[index].enabled:
                    self.current.selected_index = index
                    break
        return self.current

    def enter_text(self, text: str) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM and text:
            self.form_draft.append_text(text)
            self.refresh_current()
        elif self.current.name == ScreenName.LOG_INTERACTION_FORM and text:
            self.interaction_draft.append_text(text)
            self.refresh_current()
        elif self.current.name == ScreenName.EDIT_FIELD_FORM and text:
            self.edit_field_draft.append_text(text)
            self.refresh_current()
        elif self.current.name == ScreenName.RAW_NOTE_FORM and text:
            self.raw_note_draft.append_text(text)
            self.refresh_current()
        elif self.current.name == ScreenName.CONTACT_FORM and text:
            self.contact_draft.append_text(text)
            self.refresh_current()
        elif self.current.name == ScreenName.OPEN_LOOP_FORM and text:
            self.open_loop_draft.append_text(text)
            self.refresh_current()
        return self.current

    def backspace(self) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM:
            self.form_draft.backspace()
            self.refresh_current()
        elif self.current.name == ScreenName.LOG_INTERACTION_FORM:
            self.interaction_draft.backspace()
            self.refresh_current()
        elif self.current.name == ScreenName.EDIT_FIELD_FORM:
            self.edit_field_draft.backspace()
            self.refresh_current()
        elif self.current.name == ScreenName.RAW_NOTE_FORM:
            self.raw_note_draft.backspace()
            self.refresh_current()
        elif self.current.name == ScreenName.CONTACT_FORM:
            self.contact_draft.backspace()
            self.refresh_current()
        elif self.current.name == ScreenName.OPEN_LOOP_FORM:
            self.open_loop_draft.backspace()
            self.refresh_current()
        return self.current

    def tab_field(self, *, backwards: bool = False) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM:
            if backwards:
                self.form_draft.previous_field()
            else:
                self.form_draft.next_field()
            self.refresh_current()
        elif self.current.name == ScreenName.LOG_INTERACTION_FORM:
            if backwards:
                self.interaction_draft.previous_field()
            else:
                self.interaction_draft.next_field()
            self.refresh_current()
        elif self.current.name == ScreenName.CONTACT_FORM:
            if backwards:
                self.contact_draft.previous_field()
            else:
                self.contact_draft.next_field()
            self.refresh_current()
        elif self.current.name == ScreenName.OPEN_LOOP_FORM:
            if backwards:
                self.open_loop_draft.previous_field()
            else:
                self.open_loop_draft.next_field()
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
            if item.target == "log_interaction":
                self.interaction_draft = InteractionDraft(person_id=item.payload["person_id"])
                return NavigationResult(self.push(self.build_log_interaction_form()))
            if item.target == "edit_profile":
                return NavigationResult(self.push(self.build_edit_profile_list(item.payload["person_id"])))
            if item.target == "edit_field":
                self.edit_field_draft = EditFieldDraft(
                    person_id=item.payload["person_id"],
                    field_key=item.payload["field_key"],
                    label=item.label,
                    value=item.payload.get("current_value", ""),
                )
                return NavigationResult(self.push(self.build_edit_field_form()))
            if item.target == "append_raw_note":
                self.raw_note_draft = RawNoteDraft(person_id=item.payload["person_id"])
                return NavigationResult(self.push(self.build_raw_note_form()))
            if item.target == "add_contact":
                self.contact_draft = ContactDraft(person_id=item.payload["person_id"])
                return NavigationResult(self.push(self.build_contact_form()))
            if item.target == "add_open_loop":
                self.open_loop_draft = OpenLoopDraft(person_id=item.payload["person_id"])
                return NavigationResult(self.push(self.build_open_loop_form()))
            self.form_draft = PersonFormDraft()
            return NavigationResult(self.push(self.build_add_person_form()))
        if item.kind == ItemKind.SAVE_FORM:
            if self.current.name == ScreenName.LOG_INTERACTION_FORM:
                return NavigationResult(self.save_interaction_form())
            if self.current.name == ScreenName.EDIT_FIELD_FORM:
                return NavigationResult(self.save_edit_field_form())
            if self.current.name == ScreenName.RAW_NOTE_FORM:
                return NavigationResult(self.save_raw_note_form())
            if self.current.name == ScreenName.CONTACT_FORM:
                return NavigationResult(self.save_contact_form())
            if self.current.name == ScreenName.OPEN_LOOP_FORM:
                return NavigationResult(self.save_open_loop_form())
            return NavigationResult(self.save_person_form())
        if item.kind == ItemKind.ACTION:
            return NavigationResult(self.run_action(item))
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
        if self.current.name == ScreenName.LOG_INTERACTION_FORM and self.interaction_draft.has_values():
            self.interaction_draft = InteractionDraft()
            return self.pop()
        if self.current.name in {
            ScreenName.EDIT_PROFILE_LIST,
            ScreenName.EDIT_FIELD_FORM,
            ScreenName.RAW_NOTE_FORM,
            ScreenName.CONTACT_FORM,
            ScreenName.OPEN_LOOP_FORM,
            ScreenName.LOOP_DETAIL,
            ScreenName.SUGGESTION_DETAIL,
            ScreenName.DELETE_CONFIRM,
        }:
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
        if name == ScreenName.SUGGESTIONS:
            return self.push(self.build_suggestions())
        if name == ScreenName.EXIT_CONFIRM:
            return self.push(self.build_exit_confirm())
        return self.push(self.build_error("Unknown screen."))

    def open_dossier(self, person_id: str) -> ScreenState:
        from netops.tui.screens import dossier_screen

        try:
            dossier = self.services.people.dossier(person_id)
            if hasattr(self.services, "suggestions"):
                dossier.suggestions = self.services.suggestions.for_dossier(person_id)
            return self.push(dossier_screen(dossier))
        except Exception as exc:
            return self.push(self.build_error(f"Could not load dossier: {exc}"))

    def replace_with_dossier(self, person_id: str) -> ScreenState:
        from netops.tui.screens import dossier_screen

        dossier = self.services.people.dossier(person_id)
        if hasattr(self.services, "suggestions"):
            dossier.suggestions = self.services.suggestions.for_dossier(person_id)
        self.current = dossier_screen(dossier)
        return self.current

    def save_person_form(self) -> ScreenState:
        if not self.form_draft.validate():
            self.refresh_current()
            return self.current
        self.services.people.create_person(
            name=self.form_draft.name.strip(),
            alias=self.form_draft.alias.strip() or None,
            role=self.form_draft.role.strip() or None,
            organization=self.form_draft.organization.strip() or None,
            location=self.form_draft.location.strip() or None,
            birthday=self.form_draft.birthday.strip() or None,
            email=self.form_draft.email.strip() or None,
            phone=self.form_draft.phone.strip() or None,
            relationship_type=self.form_draft.relationship_type.strip() or None,
            relationship_strength=self.form_draft.relationship_strength.strip() or None,
            tags=self.form_draft.tags_list(),
            notes=self.form_draft.notes.strip() or None,
            interests=self.form_draft.interests_list(),
            communication_style=self.form_draft.communication_style.strip() or None,
            preferences_notes=self.form_draft.preferences_notes.strip() or None,
            signals=self.form_draft.signals_list(),
            contacts=[
                {"kind": "social", "label": "LinkedIn", "value": self.form_draft.linkedin.strip()},
                {"kind": "social", "label": "GitHub", "value": self.form_draft.github.strip()},
                {"kind": "social", "label": "Other", "value": self.form_draft.other_social.strip()},
            ],
        )
        self.form_draft = PersonFormDraft()
        self.current = self.build_people_list()
        self.stack = [self.build_main_menu()]
        return self.current

    def save_interaction_form(self) -> ScreenState:
        if not self.interaction_draft.validate():
            self.refresh_current()
            return self.current
        self.services.interactions.log_interaction(
            self.interaction_draft.person_id,
            occurred_on=date.fromisoformat(self.interaction_draft.occurred_on.strip()),
            interaction_type=self.interaction_draft.interaction_type.strip(),
            notes=self.interaction_draft.notes.strip(),
            follow_up=self.interaction_draft.follow_up.strip() or None,
            due_on=date.fromisoformat(self.interaction_draft.due_on.strip()) if self.interaction_draft.due_on.strip() else None,
        )
        person_id = self.interaction_draft.person_id
        self.interaction_draft = InteractionDraft()
        self.pop()
        return self.replace_with_dossier(person_id)

    def save_edit_field_form(self) -> ScreenState:
        try:
            self.services.people.update_profile_field(
                self.edit_field_draft.person_id,
                self.edit_field_draft.field_key,
                self.edit_field_draft.value,
            )
        except Exception as exc:
            self.edit_field_draft.validation_message = str(exc)
            self.refresh_current()
            return self.current
        person_id = self.edit_field_draft.person_id
        self.edit_field_draft = EditFieldDraft()
        self.pop()
        self.pop()
        return self.replace_with_dossier(person_id)

    def save_contact_form(self) -> ScreenState:
        if not self.contact_draft.validate():
            self.refresh_current()
            return self.current
        self.services.people.add_contact(
            self.contact_draft.person_id,
            kind=self.contact_draft.kind.strip() or "other",
            label=self.contact_draft.label.strip() or None,
            value=self.contact_draft.value.strip(),
        )
        person_id = self.contact_draft.person_id
        self.contact_draft = ContactDraft()
        self.pop()
        return self.replace_with_dossier(person_id)

    def save_open_loop_form(self) -> ScreenState:
        if not self.open_loop_draft.validate():
            self.refresh_current()
            return self.current
        due_on = date.fromisoformat(self.open_loop_draft.due_on.strip()) if self.open_loop_draft.due_on.strip() else None
        priority = int(self.open_loop_draft.priority.strip()) if self.open_loop_draft.priority.strip() else None
        self.services.loops.create(
            self.open_loop_draft.person_id,
            self.open_loop_draft.description.strip(),
            due_on=due_on,
            priority=priority,
        )
        person_id = self.open_loop_draft.person_id
        self.open_loop_draft = OpenLoopDraft()
        self.pop()
        return self.replace_with_dossier(person_id)

    def run_action(self, item: SelectableItem) -> ScreenState:
        action = item.target or ""
        if action.startswith("confirm_delete_"):
            return self.push(self.build_delete_confirm(item.payload))
        if action == "delete_cancel":
            return self.pop()
        if action == "delete_person":
            self.services.people.delete_person(item.payload["person_id"])
            self.current = self.build_people_list()
            self.stack = [self.build_main_menu()]
            return self.current
        if action == "delete_contact":
            person_id = self.services.people.delete_contact(item.payload["contact_id"])
            self.pop()
            return self.replace_with_dossier(person_id)
        if action == "delete_raw_note":
            person_id = self.services.people.delete_raw_note(item.payload["note_id"])
            self.pop()
            return self.replace_with_dossier(person_id)
        if action == "delete_open_loop":
            self.services.loops.delete(item.payload["loop_id"])
            self.current = self.build_open_loops()
            self.stack = [self.build_main_menu()]
            return self.current
        if action == "delete_suggestion":
            self.services.suggestions.delete(item.payload["suggestion_id"])
            self.current = self.build_suggestions()
            self.stack = [self.build_main_menu()]
            return self.current
        if action == "open_loop_detail":
            return self.push(self.build_loop_detail(item.payload["loop_id"]))
        if action == "complete_loop":
            self.services.loops.close(item.payload["loop_id"], status=OpenLoopStatus.COMPLETED.value)
            self.current = self.build_open_loops()
            return self.current
        if action == "defer_loop":
            self.services.loops.close(item.payload["loop_id"], status=OpenLoopStatus.DEFERRED.value)
            self.current = self.build_open_loops()
            return self.current
        if action == "open_suggestion_detail":
            return self.push(self.build_suggestion_detail(item.payload["suggestion_id"]))
        if action == "ignore_suggestion":
            self.services.suggestions.set_status(item.payload["suggestion_id"], SuggestionStatus.IGNORED.value)
            self.current = self.build_suggestions()
            return self.current
        if action == "complete_suggestion":
            self.services.suggestions.set_status(item.payload["suggestion_id"], SuggestionStatus.COMPLETED.value)
            self.current = self.build_suggestions()
            return self.current
        return self.current

    def save_raw_note_form(self) -> ScreenState:
        if not self.raw_note_draft.validate():
            self.refresh_current()
            return self.current
        self.services.people.append_raw_note(self.raw_note_draft.person_id, self.raw_note_draft.note.strip())
        person_id = self.raw_note_draft.person_id
        self.raw_note_draft = RawNoteDraft()
        self.pop()
        return self.replace_with_dossier(person_id)

    def refresh_current(self) -> ScreenState:
        if self.current.name == ScreenName.ADD_PERSON_FORM:
            self.current = self.build_add_person_form()
        elif self.current.name == ScreenName.LOG_INTERACTION_FORM:
            self.current = self.build_log_interaction_form()
        elif self.current.name == ScreenName.EDIT_FIELD_FORM:
            self.current = self.build_edit_field_form()
        elif self.current.name == ScreenName.RAW_NOTE_FORM:
            self.current = self.build_raw_note_form()
        elif self.current.name == ScreenName.CONTACT_FORM:
            self.current = self.build_contact_form()
        elif self.current.name == ScreenName.OPEN_LOOP_FORM:
            self.current = self.build_open_loop_form()
        elif self.current.name == ScreenName.PEOPLE_LIST:
            selected = self.current.selected_index
            self.current = self.build_people_list()
            self.current.selected_index = min(selected, max(0, len(self.current.items) - 1))
        return self.current

    def build_people_list(self) -> ScreenState:
        from netops.tui.screens import people_list_screen

        if hasattr(self.services.people, "grouped_directory_rows"):
            return people_list_screen(self.services.people.grouped_directory_rows())
        return people_list_screen(self.services.people.directory_rows())

    def build_overview(self) -> ScreenState:
        from netops.tui.screens import overview_screen

        return overview_screen(self.services.people.dashboard())

    def build_open_loops(self) -> ScreenState:
        from netops.tui.screens import open_loops_screen

        return open_loops_screen(self.services.loops.list())

    def build_suggestions(self) -> ScreenState:
        from netops.tui.screens import suggestions_screen

        return suggestions_screen(self.services.suggestions.generate(include_low_priority=True))

    def build_loop_detail(self, loop_id: str) -> ScreenState:
        from netops.tui.screens import loop_detail_screen

        return loop_detail_screen(self.services.loops.repository.get_open_loop(loop_id))

    def build_suggestion_detail(self, suggestion_id: str) -> ScreenState:
        from netops.tui.screens import suggestion_detail_screen

        return suggestion_detail_screen(self.services.suggestions.repository.get_suggestion(suggestion_id))

    def build_add_person_form(self) -> ScreenState:
        from netops.tui.screens import add_person_form_screen

        return add_person_form_screen(self.form_draft)

    def build_log_interaction_form(self) -> ScreenState:
        from netops.tui.screens import log_interaction_form_screen

        return log_interaction_form_screen(self.interaction_draft)

    def build_edit_profile_list(self, person_id: str) -> ScreenState:
        from netops.tui.screens import edit_profile_list_screen

        return edit_profile_list_screen(person_id, self.services.people.editable_fields(person_id))

    def build_edit_field_form(self) -> ScreenState:
        from netops.tui.screens import edit_field_form_screen

        return edit_field_form_screen(self.edit_field_draft)

    def build_raw_note_form(self) -> ScreenState:
        from netops.tui.screens import raw_note_form_screen

        return raw_note_form_screen(self.raw_note_draft)

    def build_contact_form(self) -> ScreenState:
        from netops.tui.screens import contact_form_screen

        return contact_form_screen(self.contact_draft)

    def build_open_loop_form(self) -> ScreenState:
        from netops.tui.screens import open_loop_form_screen

        return open_loop_form_screen(self.open_loop_draft)

    def build_delete_confirm(self, payload: dict[str, Any]) -> ScreenState:
        from netops.tui.screens import delete_confirm_screen

        return delete_confirm_screen(payload)

    def build_exit_confirm(self) -> ScreenState:
        from netops.tui.screens import exit_confirm_screen

        return exit_confirm_screen()

    def build_error(self, message: str) -> ScreenState:
        from netops.tui.screens import error_screen

        return error_screen(message)
