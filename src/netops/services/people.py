from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from netops.domain.models import Person, PersonContact, RawNoteEntry, Relationship
from netops.domain.validation import (
    AmbiguousMatchError,
    NotFoundError,
    UserInputError,
    normalize_relationship_strength,
    normalize_text_list,
)
from netops.storage.repositories import NetOpsRepository


@dataclass(frozen=True, slots=True)
class EditableField:
    key: str
    label: str
    section: str
    value_type: str
    current_value: str


class PeopleService:
    def __init__(self, repository: NetOpsRepository) -> None:
        self.repository = repository

    def create_person(
        self,
        *,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        organization: str | None = None,
        tags: list[str] | None = None,
        notes: str | None = None,
        alias: str | None = None,
        role: str | None = None,
        location: str | None = None,
        relationship_type: str | None = None,
        relationship_strength: str | None = None,
        birthday: str | None = None,
        interests: list[str] | str | None = None,
        communication_style: str | None = None,
        preferences_notes: str | None = None,
        signals: list[str] | str | None = None,
        contacts: list[dict[str, str | None]] | None = None,
    ) -> Person:
        person = self.repository.add_person(
            Person(
                display_name=name,
                primary_email=email,
                primary_phone=phone,
                organization=organization,
                tags=tags or [],
                relationship_notes=notes,
                alias=alias,
                role=role,
                location=location,
                relationship_type=relationship_type,
                relationship_strength=relationship_strength,
                birthday=birthday,
                interests=interests or [],
                communication_style=communication_style,
                preferences_notes=preferences_notes,
                signals=signals or [],
            )
        )
        default_contacts = [
            {"kind": "email", "label": "primary", "value": email},
            {"kind": "phone", "label": "primary", "value": phone},
        ]
        for contact in [*default_contacts, *(contacts or [])]:
            value = (contact.get("value") or "").strip()
            if value:
                self.add_contact(
                    person.id,
                    kind=(contact.get("kind") or "other").strip(),
                    value=value,
                    label=(contact.get("label") or "").strip() or None,
                )
        return person

    def list_people(self, *, tag: str | None = None, search: str | None = None) -> list[Person]:
        return self.repository.list_people(tag=tag, search=search)

    def resolve_person(self, query: str) -> Person:
        try:
            return self.repository.get_person(query)
        except NotFoundError:
            pass
        matches = [person for person in self.repository.list_people() if person.display_name.lower() == query.lower()]
        if not matches:
            matches = [
                person for person in self.repository.list_people() if query.lower() in person.display_name.lower()
            ]
        if not matches:
            raise NotFoundError(f"No person matched '{query}'. Add them first with `netops people add`.")
        if len(matches) > 1:
            details = ", ".join(f"{person.display_name} ({person.id[:8]})" for person in matches)
            raise AmbiguousMatchError(f"More than one person matched '{query}': {details}. Use an id.")
        return matches[0]

    def add_relationship(
        self,
        person_query: str,
        *,
        relationship_type: str,
        related_person_query: str | None = None,
        notes: str | None = None,
        strength: str | None = None,
    ) -> Relationship:
        person = self.resolve_person(person_query)
        related_person_id = self.resolve_person(related_person_query).id if related_person_query else None
        return self.repository.add_relationship(
            Relationship(
                person_id=person.id,
                related_person_id=related_person_id,
                relationship_type=relationship_type,
                strength=strength,
                notes=notes,
            )
        )

    def dashboard(self):
        return self.repository.dashboard_summary()

    def dossier(self, person_query: str):
        person = self.resolve_person(person_query)
        return self.repository.dossier(person.id)

    def append_raw_note(self, person_query: str, note: str, *, source: str = "dossier") -> RawNoteEntry:
        person = self.resolve_person(person_query)
        return self.repository.add_person_note(RawNoteEntry(person_id=person.id, note=note, source=source))

    def add_contact(self, person_query: str, *, kind: str, value: str, label: str | None = None) -> PersonContact:
        person = self.resolve_person(person_query)
        clean_value = value.strip()
        if not clean_value:
            raise UserInputError("Contact value is required.")
        return self.repository.add_person_contact(
            PersonContact(
                person_id=person.id,
                kind=kind.strip().lower() or "other",
                label=label.strip() if label else None,
                value=clean_value,
            )
        )

    def delete_person(self, person_query: str) -> None:
        person = self.resolve_person(person_query)
        self.repository.delete_person(person.id)

    def delete_contact(self, contact_id: str) -> str:
        contact = self.repository.get_person_contact(contact_id)
        self.repository.delete_person_contact(contact_id)
        return contact.person_id

    def delete_raw_note(self, note_id: str) -> str:
        note = self.repository.get_person_note(note_id)
        self.repository.delete_person_note(note_id)
        return note.person_id

    def editable_fields(self, person_query: str) -> list[EditableField]:
        person = self.resolve_person(person_query)
        specs = [
            ("display_name", "Name", "Identity", "text"),
            ("alias", "Alias", "Identity", "text"),
            ("organization", "Organization", "Identity", "text"),
            ("role", "Role", "Identity", "text"),
            ("location", "Location", "Identity", "text"),
            ("relationship_type", "Relationship Type", "Relationship", "text"),
            ("relationship_strength", "Relationship Strength", "Relationship", "strength"),
            ("birthday", "Birthday", "Personal Intelligence", "date"),
            ("interests", "Interests", "Personal Intelligence", "list"),
            ("communication_style", "Communication Style", "Personal Intelligence", "text"),
            ("preferences_notes", "Preferences Notes", "Personal Intelligence", "text"),
            ("signals", "Signals", "Opportunity", "list"),
        ]
        fields: list[EditableField] = []
        for key, label, section, value_type in specs:
            raw_value = getattr(person, key)
            if isinstance(raw_value, list):
                value = ", ".join(raw_value)
            else:
                value = raw_value or ""
            fields.append(EditableField(key, label, section, value_type, value))
        return fields

    def update_profile_field(self, person_query: str, key: str, value: Any) -> Person:
        allowed = {field.key: field.value_type for field in self.editable_fields(person_query)}
        if key not in allowed:
            raise UserInputError(f"Unknown editable field: {key}.")
        person = self.resolve_person(person_query)
        value_type = allowed[key]
        if key == "display_name" and not str(value).strip():
            raise UserInputError("Name is required.")
        if value_type == "list":
            normalized: Any = normalize_text_list(value)
        elif value_type == "strength":
            normalized = normalize_relationship_strength(value)
        else:
            normalized = str(value).strip() or None
        setattr(person, key, normalized)
        return self.repository.update_person(person)

    def directory_rows(self) -> list[dict[str, str]]:
        rows = []
        for person in self.repository.list_people():
            interactions = self.repository.list_interactions(person.id, limit=1)
            loops = self.repository.list_open_loops(person.id)
            rows.append(
                {
                    "id": person.id,
                    "name": person.display_name,
                    "organization": person.organization or "",
                    "tags": ", ".join(person.tags),
                    "last_interaction": interactions[0].occurred_on.isoformat() if interactions else "",
                    "open_loops": str(len([loop for loop in loops if loop.status.value in {"open", "deferred"}])),
                }
            )
        return rows

    def grouped_directory_rows(self) -> list[dict[str, str]]:
        grouped: list[dict[str, str]] = []
        current_header = None
        for row in self.directory_rows():
            stripped = row["name"].strip()
            first = stripped[:1].upper()
            header = first if first.isalpha() else "#"
            if header != current_header:
                grouped.append({"kind": "header", "name": header, "id": "", "organization": "", "tags": "", "last_interaction": "", "open_loops": ""})
                current_header = header
            grouped.append({"kind": "person", **row})
        return grouped
