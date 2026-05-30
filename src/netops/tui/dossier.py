from __future__ import annotations

from dataclasses import dataclass

from netops.domain.models import Dossier
from netops.tui.state import ItemKind, SelectableItem


@dataclass(frozen=True, slots=True)
class DossierSection:
    title: str
    rows: list[str]


def _unset(value: object) -> str:
    if value is None or value == "" or value == []:
        return "unset"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "unset"
    return str(value)


def _join_fields(*fields: tuple[str, object]) -> str:
    return " | ".join(f"{label}: {_unset(value)}" for label, value in fields)


def build_dossier_sections(dossier: Dossier) -> list[DossierSection]:
    person = dossier.person
    recent = dossier.recent_interactions[:3]
    active_loops = [loop for loop in dossier.open_loops if loop.status.value in {"open", "deferred"}]
    suggestions = dossier.suggestions[:3]
    contact_rows = [
        f"{contact.kind.title()} ({contact.label or 'default'}): {contact.value}" for contact in dossier.contacts
    ]
    if not contact_rows:
        legacy_contacts = []
        if person.primary_email:
            legacy_contacts.append(f"Email (primary): {person.primary_email}")
        if person.primary_phone:
            legacy_contacts.append(f"Phone (primary): {person.primary_phone}")
        contact_rows = legacy_contacts or ["No contact methods yet"]
    return [
        DossierSection(
            "Identity",
            [
                _join_fields(("Name", person.display_name), ("Alias", person.alias)),
                _join_fields(("Organization", person.organization), ("Role", person.role)),
                _join_fields(("Location", person.location), ("Tags", person.tags)),
            ],
        ),
        DossierSection("Contact", contact_rows),
        DossierSection(
            "Relationship",
            [
                _join_fields(("Type", person.relationship_type), ("Strength", person.relationship_strength)),
                f"Notes: {_unset(person.relationship_notes)}",
            ],
        ),
        DossierSection(
            "Personal Intelligence",
            [
                _join_fields(("Birthday", person.birthday), ("Interests", person.interests)),
                f"Communication: {_unset(person.communication_style)}",
                f"Preferences: {_unset(person.preferences_notes)}",
                f"Signals: {_unset(person.signals)}",
            ],
        ),
        DossierSection(
            "Interaction",
            [
                _join_fields(
                    ("Last contact", dossier.last_contact.isoformat() if dossier.last_contact else None),
                    ("Evaluations", len(dossier.evaluations)),
                ),
                *(f"{interaction.occurred_on.isoformat()} {interaction.interaction_type}: {interaction.notes}" for interaction in recent[:1]),
            ],
        ),
        DossierSection(
            "Opportunity",
            [
                *(f"Commitment: {loop.description}" for loop in active_loops[:2]),
                *(f"Suggestion: {suggestion.action_text}" for suggestion in suggestions[:1]),
            ]
            or ["No active commitments or suggestions"],
        ),
        DossierSection(
            "Raw Notes",
            [f"{note.created_at}: {note.note}" for note in dossier.raw_notes[-1:]] or ["No raw notes"],
        ),
    ]


def dossier_body(dossier: Dossier) -> list[str]:
    body: list[str] = []
    for section in build_dossier_sections(dossier):
        if body:
            body.append(" " + "-" * 68)
        body.append(f"[{section.title}]")
        body.extend(section.rows)
    return body


def dossier_actions(person_id: str) -> list[SelectableItem]:
    return [
        SelectableItem("Log Interaction", ItemKind.OPEN_FORM, target="log_interaction", payload={"person_id": person_id}),
        SelectableItem("Add Follow-Up / Open Loop", ItemKind.OPEN_FORM, target="add_open_loop", payload={"person_id": person_id}),
        SelectableItem("Edit Profile", ItemKind.OPEN_FORM, target="edit_profile", payload={"person_id": person_id}),
        SelectableItem("Add Contact Method", ItemKind.OPEN_FORM, target="add_contact", payload={"person_id": person_id}),
        SelectableItem("Append Raw Note", ItemKind.OPEN_FORM, target="append_raw_note", payload={"person_id": person_id}),
        SelectableItem(
            "Delete Person",
            ItemKind.ACTION,
            target="confirm_delete_person",
            payload={
                "kind": "person",
                "label": "person",
                "description": "Delete this person and all related dossier data permanently?",
                "confirm_target": "delete_person",
                "person_id": person_id,
            },
        ),
        SelectableItem("Back", ItemKind.CANCEL, hint="return to People List"),
    ]


def dossier_items(dossier: Dossier) -> list[SelectableItem]:
    items: list[SelectableItem] = []
    for section in build_dossier_sections(dossier):
        if items:
            items.append(SelectableItem(" " + "-" * 68, ItemKind.NOOP))
        items.append(SelectableItem(f"[{section.title}]", ItemKind.NOOP))
        if section.title == "Contact" and dossier.contacts:
            for contact in dossier.contacts:
                label = f"{contact.kind.title()} ({contact.label or 'default'}): {contact.value}"
                items.append(
                    SelectableItem(
                        label,
                        ItemKind.ACTION,
                        target="confirm_delete_contact",
                        hint="Enter to delete",
                        payload={
                            "kind": "contact",
                            "label": label,
                            "description": "Delete this contact method permanently?",
                            "confirm_target": "delete_contact",
                            "contact_id": contact.id,
                        },
                    )
                )
            continue
        if section.title == "Raw Notes" and dossier.raw_notes:
            for note in dossier.raw_notes:
                label = f"{note.created_at}: {note.note}"
                items.append(
                    SelectableItem(
                        label,
                        ItemKind.ACTION,
                        target="confirm_delete_raw_note",
                        hint="Enter to delete",
                        payload={
                            "kind": "raw note",
                            "label": label,
                            "description": "Delete this raw note permanently?",
                            "confirm_target": "delete_raw_note",
                            "note_id": note.id,
                        },
                    )
                )
            continue
        items.extend(SelectableItem(line, ItemKind.NOOP) for line in section.rows)
    items.extend(
        [
            SelectableItem(" " + "-" * 68, ItemKind.NOOP),
            SelectableItem("[Actions]", ItemKind.NOOP),
            *dossier_actions(dossier.person.id),
        ]
    )
    return items
