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


def build_dossier_sections(dossier: Dossier) -> list[DossierSection]:
    person = dossier.person
    recent = dossier.recent_interactions[:3]
    active_loops = [loop for loop in dossier.open_loops if loop.status.value in {"open", "deferred"}]
    suggestions = dossier.suggestions[:3]
    return [
        DossierSection(
            "Identity",
            [
                f"Name: {_unset(person.display_name)}",
                f"Alias: {_unset(person.alias)}",
                f"Organization: {_unset(person.organization)}",
                f"Role: {_unset(person.role)}",
                f"Location: {_unset(person.location)}",
            ],
        ),
        DossierSection(
            "Relationship",
            [
                f"Type: {_unset(person.relationship_type)}",
                f"Strength: {_unset(person.relationship_strength)}",
                f"Notes: {_unset(person.relationship_notes)}",
            ],
        ),
        DossierSection(
            "Personal Intelligence",
            [
                f"Birthday: {_unset(person.birthday)}",
                f"Interests: {_unset(person.interests)}",
                f"Communication: {_unset(person.communication_style)}",
                f"Preferences: {_unset(person.preferences_notes)}",
            ],
        ),
        DossierSection(
            "Interaction",
            [
                f"Last contact: {_unset(dossier.last_contact.isoformat() if dossier.last_contact else None)}",
                f"Evaluations: {len(dossier.evaluations)}",
                *(f"{interaction.occurred_on.isoformat()} {interaction.interaction_type}: {interaction.notes}" for interaction in recent),
            ],
        ),
        DossierSection(
            "Opportunity",
            [
                *(f"Commitment: {loop.description}" for loop in active_loops[:3]),
                *(f"Suggestion: {suggestion.action_text}" for suggestion in suggestions),
            ]
            or ["No active commitments or suggestions"],
        ),
        DossierSection(
            "Raw Notes",
            [f"{note.created_at}: {note.note}" for note in dossier.raw_notes] or ["No raw notes"],
        ),
    ]


def dossier_body(dossier: Dossier) -> list[str]:
    body: list[str] = []
    for section in build_dossier_sections(dossier):
        if body:
            body.append("")
        body.append(f"[{section.title}]")
        body.extend(section.rows)
    return body


def dossier_actions(person_id: str) -> list[SelectableItem]:
    return [
        SelectableItem("Log Interaction", ItemKind.OPEN_FORM, target="log_interaction", payload={"person_id": person_id}),
        SelectableItem("Edit Profile", ItemKind.OPEN_FORM, target="edit_profile", payload={"person_id": person_id}),
        SelectableItem("Append Raw Note", ItemKind.OPEN_FORM, target="append_raw_note", payload={"person_id": person_id}),
        SelectableItem("Back", ItemKind.CANCEL, hint="return to People List"),
    ]
