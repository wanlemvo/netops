from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from netops.domain.models import (
    ContactMethod,
    Opportunity,
    OpportunityPerson,
    Person,
    PersonContact,
    RawNoteEntry,
    Relationship,
    RelationshipLink,
    Signal,
    V1Person,
)
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

    def create_v1_person(
        self,
        *,
        name: str,
        alias: str | None = None,
        role: str | None = None,
        organization: str | None = None,
        location: str | None = None,
        birthday: str | None = None,
        profile_photo_path: str | None = None,
        relationship_type: str | None = None,
        relationship_status: str | None = None,
        relationship_strength: str | None = None,
        origin_story: str | None = None,
        importance_reason: str | None = None,
        dossier: str | None = None,
        interests: str | None = None,
        communication_style: str | None = None,
        preferences: str | None = None,
        current_goals: str | None = None,
        potential_value: str | None = None,
        first_met: str | None = None,
        last_contact: str | None = None,
        next_action: str | None = None,
        follow_up_date: str | None = None,
        tags: list[str] | None = None,
    ) -> V1Person:
        person = self.repository.add_v1_person(
            V1Person(
                name=name,
                alias=alias,
                role=role,
                organization=organization,
                location=location,
                birthday=birthday,
                profile_photo_path=profile_photo_path,
                relationship_type=relationship_type,
                relationship_status=relationship_status,
                relationship_strength=relationship_strength,
                origin_story=origin_story,
                importance_reason=importance_reason,
                dossier=dossier,
                interests=interests,
                communication_style=communication_style,
                preferences=preferences,
                current_goals=current_goals,
                potential_value=potential_value,
                first_met=first_met,
                last_contact=last_contact,
                next_action=next_action,
                follow_up_date=follow_up_date,
            )
        )
        if tags:
            import json
            with self.repository.connection:
                self.repository.connection.execute("UPDATE people SET tags = ? WHERE id = ?", (json.dumps(tags), person.person_id))
        return self.repository.get_v1_person(person.person_id)

    def get_v1_person(self, person_query: str) -> V1Person:
        person = self.resolve_person(person_query)
        return self.repository.get_v1_person(person.id)

    def update_v1_person_field(self, person_query: str, key: str, value: Any) -> V1Person:
        if key == "display_name":
            key = "name"
        if key == "preferences_notes":
            key = "preferences"
        allowed = {
            "name",
            "alias",
            "role",
            "organization",
            "location",
            "birthday",
            "profile_photo_path",
            "relationship_type",
            "relationship_status",
            "relationship_strength",
            "origin_story",
            "importance_reason",
            "dossier",
            "interests",
            "communication_style",
            "preferences",
            "current_goals",
            "potential_value",
            "first_met",
            "last_contact",
            "next_action",
            "follow_up_date",
        }
        if key not in allowed:
            raise UserInputError(f"Unknown V1 person field: {key}.")
        person = self.get_v1_person(person_query)
        setattr(person, key, value)
        return self.repository.update_v1_person(person)

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

    def add_contact_method(
        self,
        person_query: str,
        *,
        kind: str,
        value: str,
        label: str | None = None,
        is_primary: bool = False,
    ) -> ContactMethod:
        person = self.resolve_person(person_query)
        contact = self.repository.add_contact_method(
            ContactMethod(
                person_id=person.id,
                type=kind.strip().lower() or "other",
                label=label.strip() if label else None,
                value=value,
                is_primary=1 if is_primary else 0,
            )
        )
        if is_primary:
            contact = self.repository.set_primary_contact_method(contact.contact_method_id)
        return contact

    def list_contact_methods(self, person_query: str) -> list[ContactMethod]:
        person = self.resolve_person(person_query)
        return self.repository.list_contact_methods(person.id)

    def delete_contact_method(self, contact_method_id: str) -> str:
        contact = self.repository.get_contact_method(contact_method_id)
        self.repository.delete_contact_method(contact_method_id)
        return contact.person_id

    def set_primary_contact_method(self, contact_method_id: str) -> ContactMethod:
        return self.repository.set_primary_contact_method(contact_method_id)

    def set_profile_photo(self, person_query: str, photo_path: str, *, copy_to_assets: bool = True) -> V1Person:
        person = self.get_v1_person(person_query)
        clean_path = photo_path.strip()
        if not clean_path:
            return self.update_v1_person_field(person.person_id, "profile_photo_path", None)
        source = Path(clean_path).expanduser()
        stored_path = clean_path
        if copy_to_assets and source.exists() and source.is_file():
            assets_dir = self._profile_photo_assets_dir()
            assets_dir.mkdir(parents=True, exist_ok=True)
            destination = assets_dir / f"{person.person_id}{source.suffix.lower()}"
            shutil.copy2(source, destination)
            stored_path = str(Path("assets") / "profile_photos" / destination.name)
        return self.update_v1_person_field(person.person_id, "profile_photo_path", stored_path)

    def _profile_photo_assets_dir(self) -> Path:
        database_file = self.repository.connection.execute("PRAGMA database_list").fetchone()[2]
        if database_file:
            return Path(database_file).parent / "assets" / "profile_photos"
        netops_home = os.environ.get("NETOPS_HOME")
        if netops_home:
            return Path(netops_home) / "data" / "assets" / "profile_photos"
        db_override = os.environ.get("NETOPS_DB")
        if db_override and db_override != ":memory:":
            return Path(db_override).resolve().parent / "assets" / "profile_photos"
        return Path.home() / ".netops" / "assets" / "profile_photos"

    def add_signal(
        self,
        person_query: str,
        *,
        text: str,
        confidence: str | None = None,
        source_interaction_id: str | None = None,
        source_description: str | None = None,
    ) -> Signal:
        person = self.resolve_person(person_query)
        return self.repository.add_signal(
            Signal(
                person_id=person.id,
                signal_text=text,
                confidence=confidence,
                source_interaction_id=source_interaction_id,
                source_description=source_description,
            )
        )

    def list_signals(self, person_query: str) -> list[Signal]:
        person = self.resolve_person(person_query)
        return self.repository.list_signals(person.id)

    def add_opportunity(
        self,
        person_queries: list[str],
        *,
        title: str,
        status: str = "open",
        description: str | None = None,
        follow_up_date: str | None = None,
    ) -> Opportunity:
        if not person_queries:
            raise UserInputError("At least one person is required.")
        people = [self.resolve_person(query) for query in person_queries]
        opportunity = Opportunity(title=title, status=status, description=description, follow_up_date=follow_up_date)
        participants = [
            OpportunityPerson(
                opportunity_id=opportunity.opportunity_id,
                person_id=person.id,
                role="owner" if index == 0 else "participant",
                is_primary=1 if index == 0 else 0,
            )
            for index, person in enumerate(people)
        ]
        return self.repository.add_opportunity(opportunity, participants)

    def list_opportunities(self, person_query: str) -> list[Opportunity]:
        person = self.resolve_person(person_query)
        return self.repository.list_opportunities_for_person(person.id)

    def add_relationship_link(
        self,
        source_person_query: str,
        target_person_query: str,
        *,
        relationship_type: str,
        description: str | None = None,
    ) -> RelationshipLink:
        source = self.resolve_person(source_person_query)
        target = self.resolve_person(target_person_query)
        return self.repository.add_relationship_link(
            RelationshipLink(
                source_entity_type="person",
                source_entity_id=source.id,
                target_entity_type="person",
                target_entity_id=target.id,
                relationship_type=relationship_type,
                description=description,
            )
        )

    def list_relationship_links(self, person_query: str) -> list[RelationshipLink]:
        person = self.resolve_person(person_query)
        return self.repository.list_relationship_links_for_entity("person", person.id)

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
        v1_person = self.repository.get_v1_person(person.id)
        specs = [
            ("name", "Name", "Identity", "text"),
            ("alias", "Alias", "Identity", "text"),
            ("organization", "Organization", "Identity", "text"),
            ("role", "Role", "Identity", "text"),
            ("location", "Location", "Identity", "text"),
            ("birthday", "Birthday", "Identity", "date"),
            ("profile_photo_path", "Profile Photo", "Identity", "text"),
            ("relationship_type", "Relationship Type", "Relationship", "text"),
            ("relationship_status", "Relationship Status", "Relationship", "text"),
            ("relationship_strength", "Relationship Strength", "Relationship", "strength"),
            ("origin_story", "Origin Story", "Relationship", "text"),
            ("importance_reason", "Importance Reason", "Relationship", "text"),
            ("dossier", "Dossier", "Dossier", "text"),
            ("interests", "Interests", "Personal Intelligence", "text"),
            ("communication_style", "Communication Style", "Personal Intelligence", "text"),
            ("preferences", "Preferences", "Personal Intelligence", "text"),
            ("current_goals", "Current Goals", "Strategic Context", "text"),
            ("potential_value", "Potential Value", "Strategic Context", "text"),
            ("first_met", "First Met", "Network Ops", "date"),
            ("last_contact", "Last Contact", "Network Ops", "date"),
            ("next_action", "Next Action", "Network Ops", "text"),
            ("follow_up_date", "Follow-Up Date", "Network Ops", "date"),
        ]
        fields: list[EditableField] = []
        for key, label, section, value_type in specs:
            raw_value = getattr(v1_person, key, None)
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
        if key == "name" and not str(value).strip():
            raise UserInputError("Name is required.")
        if allowed[key] == "list":
            normalized: Any = normalize_text_list(value)
        elif key == "relationship_strength":
            normalized = normalize_relationship_strength(value)
        else:
            normalized = value
        self.update_v1_person_field(person_query, key, normalized)
        return self.resolve_person(person_query)

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
