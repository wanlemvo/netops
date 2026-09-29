from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from typing import Iterable

from netops.domain.models import (
    DashboardSummary,
    ContactMethod,
    Dossier,
    Evaluation,
    EvaluationOutcome,
    Interaction,
    InteractionPerson,
    OpenLoop,
    OpenLoopStatus,
    Opportunity,
    OpportunityPerson,
    Person,
    PersonContact,
    RawNoteEntry,
    Relationship,
    RelationshipLink,
    Signal,
    SuggestedAction,
    SuggestionStatus,
    Tag,
    Tagging,
    TimelineEntry,
    V1Interaction,
    V1Person,
    now_iso,
)
from netops.domain.validation import NotFoundError, UserInputError, normalize_date_text, require_entity_type
from netops.storage.migrations import migrate
from netops.storage.casefile import CasefileRepository
from netops.storage.catalog import CatalogRepository


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _date_from_text(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _v1_date_text_from_row(value: str | None, *, allow_month: bool = False) -> str | None:
    try:
        return normalize_date_text(value, allow_month=allow_month)
    except UserInputError:
        return None


def _list_to_text(values: list[str]) -> str:
    return json.dumps(values)


def _list_from_text(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
        return [str(item).strip() for item in loaded if str(item).strip()]
    except (TypeError, json.JSONDecodeError):
        return []


def _tags_to_text(tags: list[str]) -> str:
    return json.dumps(tags)


def _tags_from_text(value: str | None) -> list[str]:
    return _list_from_text(value)


class NetOpsRepository(CasefileRepository, CatalogRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        migrate(connection)

    def person_from_row(self, row: sqlite3.Row) -> Person:
        data = dict(row)
        data["tags"] = _tags_from_text(data.get("tags"))
        data["interests"] = _list_from_text(data.get("interests"))
        data["signals"] = _list_from_text(data.get("signals"))
        return Person(**data)

    def relationship_from_row(self, row: sqlite3.Row) -> Relationship:
        return Relationship(**dict(row))

    def interaction_from_row(self, row: sqlite3.Row) -> Interaction:
        data = dict(row)
        data["occurred_on"] = _date_from_text(data["occurred_on"])
        return Interaction(**data)

    def open_loop_from_row(self, row: sqlite3.Row) -> OpenLoop:
        data = dict(row)
        data["due_on"] = _date_from_text(data.get("due_on"))
        return OpenLoop(**data)

    def suggestion_from_row(self, row: sqlite3.Row) -> SuggestedAction:
        return SuggestedAction(**dict(row))

    def evaluation_from_row(self, row: sqlite3.Row) -> Evaluation:
        data = dict(row)
        data["evaluated_on"] = _date_from_text(data["evaluated_on"])
        return Evaluation(**data)

    def raw_note_from_row(self, row: sqlite3.Row) -> RawNoteEntry:
        return RawNoteEntry(**dict(row))

    def contact_from_row(self, row: sqlite3.Row) -> PersonContact:
        return PersonContact(**dict(row))

    def v1_person_from_row(self, row: sqlite3.Row) -> V1Person:
        data = dict(row)
        return V1Person(
            person_id=data.get("person_id") or data["id"],
            name=data.get("name") or data["display_name"],
            alias=data.get("alias"),
            role=data.get("role"),
            organization=data.get("organization"),
            location=data.get("location"),
            birthday=_v1_date_text_from_row(data.get("birthday"), allow_month=True),
            profile_photo_path=data.get("profile_photo_path"),
            relationship_type=data.get("relationship_type"),
            relationship_status=data.get("relationship_status"),
            relationship_strength=data.get("relationship_strength"),
            origin_story=data.get("origin_story"),
            importance_reason=data.get("importance_reason"),
            dossier=data.get("dossier"),
            interests=data.get("interests"),
            communication_style=data.get("communication_style"),
            preferences=data.get("preferences") or data.get("preferences_notes"),
            current_goals=data.get("current_goals"),
            potential_value=data.get("potential_value"),
            first_met=_v1_date_text_from_row(data.get("first_met"), allow_month=True),
            last_contact=_v1_date_text_from_row(data.get("last_contact"), allow_month=True),
            next_action=data.get("next_action"),
            follow_up_date=_v1_date_text_from_row(data.get("follow_up_date"), allow_month=True),
            follow_up_completed_at=data.get("follow_up_completed_at"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            archived_at=data.get("archived_at"),
        )

    def contact_method_from_row(self, row: sqlite3.Row) -> ContactMethod:
        return ContactMethod(**dict(row))

    def v1_interaction_from_row(self, row: sqlite3.Row) -> V1Interaction:
        data = dict(row)
        return V1Interaction(
            interaction_id=data.get("interaction_id") or data["id"],
            interaction_date=_v1_date_text_from_row(data.get("interaction_date") or data["occurred_on"]) or date.today().isoformat(),
            interaction_type=data.get("interaction_type"),
            summary=data.get("summary") or data.get("notes"),
            takeaways=data.get("takeaways"),
            action_items=data.get("action_items"),
            sentiment=data.get("sentiment"),
            follow_up_required=data.get("follow_up_required", 0),
            follow_up_date=_v1_date_text_from_row(data.get("follow_up_date")),
            follow_up_completed_at=data.get("follow_up_completed_at"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            archived_at=data.get("archived_at"),
        )

    def interaction_person_from_row(self, row: sqlite3.Row) -> InteractionPerson:
        return InteractionPerson(**dict(row))

    def signal_from_row(self, row: sqlite3.Row) -> Signal:
        return Signal(**dict(row))

    def opportunity_from_row(self, row: sqlite3.Row) -> Opportunity:
        data = dict(row)
        data["follow_up_date"] = _v1_date_text_from_row(data.get("follow_up_date"))
        return Opportunity(**data)

    def opportunity_person_from_row(self, row: sqlite3.Row) -> OpportunityPerson:
        return OpportunityPerson(**dict(row))

    def relationship_link_from_row(self, row: sqlite3.Row) -> RelationshipLink:
        return RelationshipLink(**dict(row))

    def tag_from_row(self, row: sqlite3.Row) -> Tag:
        return Tag(**dict(row))

    def tagging_from_row(self, row: sqlite3.Row) -> Tagging:
        return Tagging(**dict(row))

    def add_person(self, person: Person) -> Person:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO people (
                    id, display_name, given_name, family_name, primary_email, primary_phone,
                    organization, tags, relationship_notes, alias, role, location, relationship_type,
                    relationship_strength, birthday, interests, communication_style, preferences_notes,
                    signals, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    person.id,
                    person.display_name,
                    person.given_name,
                    person.family_name,
                    person.primary_email,
                    person.primary_phone,
                    person.organization,
                    _tags_to_text(person.tags),
                    person.relationship_notes,
                    person.alias,
                    person.role,
                    person.location,
                    person.relationship_type,
                    person.relationship_strength,
                    person.birthday,
                    _list_to_text(person.interests),
                    person.communication_style,
                    person.preferences_notes,
                    _list_to_text(person.signals),
                    person.created_at,
                    person.updated_at,
                ),
            )
            self.connection.execute(
                "UPDATE people SET person_id = COALESCE(person_id, id), name = COALESCE(name, display_name) WHERE id = ?",
                (person.id,),
            )
            if person.primary_email:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO contact_methods (
                        contact_method_id, person_id, type, label, value, normalized_value,
                        is_primary, created_at, updated_at
                    ) VALUES (?, ?, 'email', 'primary', ?, ?, 1, ?, ?)
                    """,
                    (
                        f"{person.id}-email",
                        person.id,
                        person.primary_email,
                        person.primary_email.strip().lower(),
                        person.created_at,
                        person.updated_at,
                    ),
                )
            if person.primary_phone:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO contact_methods (
                        contact_method_id, person_id, type, label, value, normalized_value,
                        is_primary, created_at, updated_at
                    ) VALUES (?, ?, 'phone', 'primary', ?, ?, 1, ?, ?)
                    """,
                    (
                        f"{person.id}-phone",
                        person.id,
                        person.primary_phone,
                        person.primary_phone.strip(),
                        person.created_at,
                        person.updated_at,
                    ),
                )
        return person

    def add_v1_person(self, person: V1Person) -> V1Person:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO people (
                    id, person_id, display_name, name, alias, role, organization, location, birthday,
                    profile_photo_path, relationship_type, relationship_status, relationship_strength,
                    origin_story, importance_reason, dossier, interests, communication_style, preferences,
                    current_goals, potential_value, first_met, last_contact, next_action, follow_up_date,
                    tags, created_at, updated_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    person.person_id,
                    person.person_id,
                    person.name,
                    person.name,
                    person.alias,
                    person.role,
                    person.organization,
                    person.location,
                    person.birthday,
                    person.profile_photo_path,
                    person.relationship_type,
                    person.relationship_status,
                    person.relationship_strength,
                    person.origin_story,
                    person.importance_reason,
                    person.dossier,
                    person.interests or "",
                    person.communication_style,
                    person.preferences,
                    person.current_goals,
                    person.potential_value,
                    person.first_met,
                    person.last_contact,
                    person.next_action,
                    person.follow_up_date,
                    "[]",
                    person.created_at,
                    person.updated_at,
                    person.archived_at,
                ),
            )
        return person

    def update_v1_person(self, person: V1Person) -> V1Person:
        person.updated_at = now_iso()
        with self.connection:
            self.connection.execute(
                """
                UPDATE people
                SET display_name = ?, name = ?, alias = ?, role = ?, organization = ?, location = ?,
                    birthday = ?, profile_photo_path = ?, relationship_type = ?, relationship_status = ?,
                    relationship_strength = ?, origin_story = ?, importance_reason = ?, dossier = ?,
                    interests = ?, communication_style = ?, preferences = ?, current_goals = ?,
                    potential_value = ?, first_met = ?, last_contact = ?, next_action = ?,
                    follow_up_date = ?, updated_at = ?, archived_at = ?
                WHERE person_id = ? OR id = ?
                """,
                (
                    person.name,
                    person.name,
                    person.alias,
                    person.role,
                    person.organization,
                    person.location,
                    person.birthday,
                    person.profile_photo_path,
                    person.relationship_type,
                    person.relationship_status,
                    person.relationship_strength,
                    person.origin_story,
                    person.importance_reason,
                    person.dossier,
                    person.interests or "",
                    person.communication_style,
                    person.preferences,
                    person.current_goals,
                    person.potential_value,
                    person.first_met,
                    person.last_contact,
                    person.next_action,
                    person.follow_up_date,
                    person.updated_at,
                    person.archived_at,
                    person.person_id,
                    person.person_id,
                ),
            )
        return person

    def get_v1_person(self, person_id: str) -> V1Person:
        row = self.connection.execute(
            "SELECT * FROM people WHERE person_id = ? OR id = ?",
            (person_id, person_id),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"No person found for '{person_id}'.")
        return self.v1_person_from_row(row)

    def list_v1_people(self) -> list[V1Person]:
        rows = self.connection.execute(
            "SELECT * FROM people WHERE archived_at IS NULL ORDER BY lower(COALESCE(name, display_name))"
        ).fetchall()
        return [self.v1_person_from_row(row) for row in rows]

    def add_contact_method(self, contact: ContactMethod) -> ContactMethod:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO contact_methods (
                    contact_method_id, person_id, type, label, value, normalized_value,
                    is_primary, created_at, updated_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contact.contact_method_id,
                    contact.person_id,
                    contact.type,
                    contact.label,
                    contact.value,
                    contact.normalized_value or contact.value.strip().lower(),
                    contact.is_primary,
                    contact.created_at,
                    contact.updated_at,
                    contact.archived_at,
                ),
            )
        return contact

    def list_contact_methods(self, person_id: str) -> list[ContactMethod]:
        rows = self.connection.execute(
            "SELECT * FROM contact_methods WHERE person_id = ? AND archived_at IS NULL ORDER BY type, is_primary DESC, created_at",
            (person_id,),
        ).fetchall()
        return [self.contact_method_from_row(row) for row in rows]

    def get_contact_method(self, contact_method_id: str) -> ContactMethod:
        row = self.connection.execute(
            "SELECT * FROM contact_methods WHERE contact_method_id = ?",
            (contact_method_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError(f"No contact method found for '{contact_method_id}'.")
        return self.contact_method_from_row(row)

    def delete_contact_method(self, contact_method_id: str) -> None:
        contact = self.get_contact_method(contact_method_id)
        archived_at = now_iso()
        with self.connection:
            self.connection.execute(
                "UPDATE contact_methods SET archived_at = ?, updated_at = ? WHERE contact_method_id = ?",
                (archived_at, archived_at, contact_method_id),
            )
            self.connection.execute("DELETE FROM person_contacts WHERE id = ?", (contact.contact_method_id,))

    def set_primary_contact_method(self, contact_method_id: str) -> ContactMethod:
        contact = self.get_contact_method(contact_method_id)
        updated_at = now_iso()
        with self.connection:
            self.connection.execute(
                "UPDATE contact_methods SET is_primary = 0, updated_at = ? WHERE person_id = ? AND type = ?",
                (updated_at, contact.person_id, contact.type),
            )
            self.connection.execute(
                "UPDATE contact_methods SET is_primary = 1, updated_at = ? WHERE contact_method_id = ?",
                (updated_at, contact_method_id),
            )
        return self.get_contact_method(contact_method_id)

    def add_v1_interaction(self, interaction: V1Interaction, people: list[InteractionPerson] | None = None) -> V1Interaction:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO interactions (
                    id, interaction_id, person_id, occurred_on, interaction_date, interaction_type, notes,
                    summary, takeaways, action_items, sentiment, follow_up_required, follow_up_date,
                    created_at, updated_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction.interaction_id,
                    interaction.interaction_id,
                    people[0].person_id if people else "",
                    interaction.interaction_date,
                    interaction.interaction_date,
                    interaction.interaction_type or "meeting",
                    interaction.summary or "",
                    interaction.summary,
                    interaction.takeaways,
                    interaction.action_items,
                    interaction.sentiment,
                    interaction.follow_up_required,
                    interaction.follow_up_date,
                    interaction.created_at,
                    interaction.updated_at,
                    interaction.archived_at,
                ),
            )
            for participant in people or []:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO interaction_people (
                        interaction_person_id, interaction_id, person_id, role, is_primary, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        participant.interaction_person_id,
                        interaction.interaction_id,
                        participant.person_id,
                        participant.role,
                        participant.is_primary,
                        participant.created_at,
                    ),
                )
        return interaction

    def list_v1_interactions_for_person(self, person_id: str) -> list[V1Interaction]:
        rows = self.connection.execute(
            """
            SELECT i.* FROM interactions i
            JOIN interaction_people ip ON ip.interaction_id = COALESCE(i.interaction_id, i.id)
            WHERE ip.person_id = ? AND i.archived_at IS NULL
            ORDER BY COALESCE(i.interaction_date, i.occurred_on) DESC, i.created_at DESC
            """,
            (person_id,),
        ).fetchall()
        return [self.v1_interaction_from_row(row) for row in rows]

    def add_signal(self, signal: Signal) -> Signal:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO signals (
                    signal_id, person_id, signal_text, confidence, source_interaction_id,
                    source_description, created_at, updated_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.signal_id,
                    signal.person_id,
                    signal.signal_text,
                    signal.confidence,
                    signal.source_interaction_id,
                    signal.source_description,
                    signal.created_at,
                    signal.updated_at,
                    signal.archived_at,
                ),
            )
        return signal

    def list_signals(self, person_id: str) -> list[Signal]:
        rows = self.connection.execute(
            "SELECT * FROM signals WHERE person_id = ? AND archived_at IS NULL ORDER BY created_at DESC",
            (person_id,),
        ).fetchall()
        return [self.signal_from_row(row) for row in rows]

    def add_opportunity(self, opportunity: Opportunity, people: list[OpportunityPerson] | None = None) -> Opportunity:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO opportunities (
                    opportunity_id, title, status, description, follow_up_date,
                    created_at, updated_at, closed_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    opportunity.opportunity_id,
                    opportunity.title,
                    opportunity.status,
                    opportunity.description,
                    opportunity.follow_up_date,
                    opportunity.created_at,
                    opportunity.updated_at,
                    opportunity.closed_at,
                    opportunity.archived_at,
                ),
            )
            for participant in people or []:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO opportunity_people (
                        opportunity_person_id, opportunity_id, person_id, role, is_primary, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        participant.opportunity_person_id,
                        opportunity.opportunity_id,
                        participant.person_id,
                        participant.role,
                        participant.is_primary,
                        participant.created_at,
                    ),
                )
        return opportunity

    def list_opportunities_for_person(self, person_id: str) -> list[Opportunity]:
        rows = self.connection.execute(
            """
            SELECT o.* FROM opportunities o
            JOIN opportunity_people op ON op.opportunity_id = o.opportunity_id
            WHERE op.person_id = ? AND o.archived_at IS NULL
            ORDER BY CASE WHEN o.follow_up_date IS NULL THEN 1 ELSE 0 END, o.follow_up_date, o.created_at DESC
            """,
            (person_id,),
        ).fetchall()
        return [self.opportunity_from_row(row) for row in rows]

    def add_relationship_link(self, link: RelationshipLink) -> RelationshipLink:
        require_entity_type(link.source_entity_type)
        require_entity_type(link.target_entity_type)
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO relationship_links (
                    relationship_link_id, source_entity_type, source_entity_id, target_entity_type,
                    target_entity_id, relationship_type, description, created_at, updated_at, archived_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    link.relationship_link_id,
                    link.source_entity_type,
                    link.source_entity_id,
                    link.target_entity_type,
                    link.target_entity_id,
                    link.relationship_type,
                    link.description,
                    link.created_at,
                    link.updated_at,
                    link.archived_at,
                ),
            )
        return link

    def list_relationship_links_for_entity(self, entity_type: str, entity_id: str) -> list[RelationshipLink]:
        entity_type = require_entity_type(entity_type)
        rows = self.connection.execute(
            """
            SELECT * FROM relationship_links
            WHERE archived_at IS NULL
              AND ((source_entity_type = ? AND source_entity_id = ?)
                OR (target_entity_type = ? AND target_entity_id = ?))
            ORDER BY created_at DESC
            """,
            (entity_type, entity_id, entity_type, entity_id),
        ).fetchall()
        return [self.relationship_link_from_row(row) for row in rows]

    def add_tag(self, tag: Tag) -> Tag:
        with self.connection:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO tags (tag_id, name, normalized_name, created_at, updated_at, archived_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tag.tag_id, tag.name, tag.normalized_name, tag.created_at, tag.updated_at, tag.archived_at),
            )
        row = self.connection.execute("SELECT * FROM tags WHERE normalized_name = ?", (tag.normalized_name,)).fetchone()
        return self.tag_from_row(row)

    def add_tagging(self, tagging: Tagging) -> Tagging:
        with self.connection:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO taggings (tagging_id, tag_id, entity_type, entity_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tagging.tagging_id, tagging.tag_id, tagging.entity_type, tagging.entity_id, tagging.created_at),
            )
        return tagging

    def list_v1_follow_ups(self) -> list[dict[str, str]]:
        person_rows = self.connection.execute(
            """
            SELECT person_id, name, next_action, follow_up_date
            FROM people
            WHERE archived_at IS NULL
              AND follow_up_completed_at IS NULL
              AND (trim(COALESCE(next_action, '')) != '' OR trim(COALESCE(follow_up_date, '')) != '')
            """
        ).fetchall()
        opportunity_rows = self.connection.execute(
            """
            SELECT o.opportunity_id, o.title, o.status, o.follow_up_date, p.name
            FROM opportunities o
            LEFT JOIN opportunity_people op ON op.opportunity_id = o.opportunity_id AND op.is_primary = 1
            LEFT JOIN people p ON p.id = op.person_id
            WHERE o.archived_at IS NULL
              AND o.follow_up_completed_at IS NULL
              AND lower(o.status) NOT IN ('closed', 'complete', 'completed', 'archived')
              AND trim(COALESCE(o.follow_up_date, '')) != ''
            """
        ).fetchall()
        rows: list[dict[str, str]] = [
            {
                "kind": "person",
                "id": row["person_id"],
                "title": row["name"] or row["person_id"],
                "action": row["next_action"] or "",
                "follow_up_date": row["follow_up_date"] or "",
                "status": "pending",
                "person": row["name"] or "",
            }
            for row in person_rows
        ]
        rows.extend(
            {
                "kind": "opportunity",
                "id": row["opportunity_id"],
                "title": row["title"],
                "action": row["title"],
                "follow_up_date": row["follow_up_date"] or "",
                "status": row["status"],
                "person": row["name"] or "",
            }
            for row in opportunity_rows
        )
        interaction_rows = self.connection.execute("""
            SELECT i.interaction_id, i.summary, i.action_items, i.follow_up_date,
                   group_concat(p.name, ', ') AS person
            FROM interactions i
            LEFT JOIN interaction_people ip ON ip.interaction_id = i.interaction_id
            LEFT JOIN people p ON p.id = ip.person_id
            WHERE i.archived_at IS NULL AND i.follow_up_completed_at IS NULL
              AND i.follow_up_required = 1
            GROUP BY i.interaction_id
        """).fetchall()
        rows.extend({"kind": "interaction", "id": row["interaction_id"],
                     "title": row["summary"] or "Interaction follow-up",
                     "action": row["action_items"] or "", "person": row["person"] or "",
                     "follow_up_date": row["follow_up_date"] or "", "status": "pending"}
                    for row in interaction_rows)
        return sorted(rows, key=lambda row: (row["follow_up_date"] == "", row["follow_up_date"], row["kind"], row["title"].lower()))

    def _follow_up_record(self, kind: str, record_id: str):
        targets = {"person": ("people", "person_id"), "interaction": ("interactions", "interaction_id"),
                   "opportunity": ("opportunities", "opportunity_id")}
        if kind not in targets:
            raise UserInputError("Unknown follow-up kind.")
        table, key = targets[kind]
        row = self.connection.execute(
            f"SELECT * FROM {table} WHERE {key} = ? AND archived_at IS NULL", (record_id,)
        ).fetchone()
        if row is None:
            raise NotFoundError("Follow-up record was not found.")
        return table, key, row

    def complete_follow_up(self, kind: str, record_id: str) -> dict:
        table, key, _ = self._follow_up_record(kind, record_id)
        with self.connection:
            self.connection.execute(
                f"UPDATE {table} SET follow_up_completed_at = COALESCE(follow_up_completed_at, ?), updated_at = ? WHERE {key} = ?",
                (now_iso(), now_iso(), record_id),
            )
        _, _, row = self._follow_up_record(kind, record_id)
        return {"kind": kind, "id": record_id, "completed_at": row["follow_up_completed_at"]}

    def reschedule_follow_up(self, kind: str, record_id: str, follow_up_date: str | None) -> dict:
        table, key, _ = self._follow_up_record(kind, record_id)
        required = ", follow_up_required = 1" if kind == "interaction" else ""
        with self.connection:
            self.connection.execute(
                f"UPDATE {table} SET follow_up_date = ?, follow_up_completed_at = NULL, updated_at = ?{required} WHERE {key} = ?",
                (follow_up_date, now_iso(), record_id),
            )
        return {"kind": kind, "id": record_id, "follow_up_date": follow_up_date, "completed_at": None}

    def update_person(self, person: Person) -> Person:
        person.updated_at = now_iso()
        with self.connection:
            self.connection.execute(
                """
                UPDATE people
                SET display_name = ?, given_name = ?, family_name = ?, primary_email = ?,
                    primary_phone = ?, organization = ?, tags = ?, relationship_notes = ?,
                    alias = ?, role = ?, location = ?, relationship_type = ?, relationship_strength = ?,
                    birthday = ?, interests = ?, communication_style = ?, preferences_notes = ?,
                    signals = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    person.display_name,
                    person.given_name,
                    person.family_name,
                    person.primary_email,
                    person.primary_phone,
                    person.organization,
                    _tags_to_text(person.tags),
                    person.relationship_notes,
                    person.alias,
                    person.role,
                    person.location,
                    person.relationship_type,
                    person.relationship_strength,
                    person.birthday,
                    _list_to_text(person.interests),
                    person.communication_style,
                    person.preferences_notes,
                    _list_to_text(person.signals),
                    person.updated_at,
                    person.id,
                ),
            )
        return person

    def get_person(self, person_id: str) -> Person:
        row = self.connection.execute("SELECT * FROM people WHERE id = ?", (person_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"No person found for '{person_id}'.")
        return self.person_from_row(row)

    def list_people(self, *, tag: str | None = None, search: str | None = None) -> list[Person]:
        rows = self.connection.execute("SELECT * FROM people ORDER BY lower(display_name)").fetchall()
        people = [self.person_from_row(row) for row in rows]
        if tag:
            people = [person for person in people if tag in person.tags]
        if search:
            needle = search.lower()
            people = [
                person
                for person in people
                if needle in person.display_name.lower()
                or needle in (person.organization or "").lower()
                or needle in (person.relationship_notes or "").lower()
            ]
        return people

    def delete_person(self, person_id: str) -> None:
        self.get_person(person_id)
        with self.connection:
            self.connection.execute("DELETE FROM people WHERE id = ?", (person_id,))

    def add_relationship(self, relationship: Relationship) -> Relationship:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO relationships (
                    id, person_id, related_person_id, relationship_type, strength, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relationship.id,
                    relationship.person_id,
                    relationship.related_person_id,
                    relationship.relationship_type,
                    relationship.strength,
                    relationship.notes,
                    relationship.created_at,
                    relationship.updated_at,
                ),
            )
            if relationship.related_person_id:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO relationship_links (
                        relationship_link_id, source_entity_type, source_entity_id, target_entity_type,
                        target_entity_id, relationship_type, description, created_at, updated_at
                    ) VALUES (?, 'person', ?, 'person', ?, ?, ?, ?, ?)
                    """,
                    (
                        relationship.id,
                        relationship.person_id,
                        relationship.related_person_id,
                        relationship.relationship_type,
                        relationship.notes,
                        relationship.created_at,
                        relationship.updated_at,
                    ),
                )
        return relationship

    def list_relationships(self, person_id: str) -> list[Relationship]:
        rows = self.connection.execute(
            "SELECT * FROM relationships WHERE person_id = ? OR related_person_id = ? ORDER BY created_at DESC",
            (person_id, person_id),
        ).fetchall()
        return [self.relationship_from_row(row) for row in rows]

    def add_interaction(self, interaction: Interaction) -> Interaction:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO interactions (
                    id, interaction_id, person_id, occurred_on, interaction_date, interaction_type,
                    notes, summary, follow_up_required, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    interaction.id,
                    interaction.id,
                    interaction.person_id,
                    _date_to_text(interaction.occurred_on),
                    _date_to_text(interaction.occurred_on),
                    interaction.interaction_type,
                    interaction.notes,
                    interaction.notes,
                    interaction.created_at,
                    interaction.updated_at,
                ),
            )
            self.connection.execute(
                """
                INSERT OR IGNORE INTO interaction_people (
                    interaction_person_id, interaction_id, person_id, role, is_primary, created_at
                ) VALUES (?, ?, ?, 'primary', 1, ?)
                """,
                (f"{interaction.id}-{interaction.person_id}", interaction.id, interaction.person_id, interaction.created_at),
            )
        return interaction

    def list_interactions(self, person_id: str | None = None, *, limit: int | None = None) -> list[Interaction]:
        sql = "SELECT * FROM interactions"
        params: list[object] = []
        if person_id:
            sql += " WHERE person_id = ?"
            params.append(person_id)
        sql += " ORDER BY occurred_on DESC, created_at DESC"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        rows = self.connection.execute(sql, params).fetchall()
        return [self.interaction_from_row(row) for row in rows]

    def get_interaction(self, interaction_id: str) -> Interaction:
        row = self.connection.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"No interaction found for '{interaction_id}'.")
        return self.interaction_from_row(row)

    def add_open_loop(self, loop: OpenLoop) -> OpenLoop:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO open_loops (
                    id, person_id, source_interaction_id, description, status, due_on, priority,
                    resolution_notes, created_at, updated_at, closed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    loop.id,
                    loop.person_id,
                    loop.source_interaction_id,
                    loop.description,
                    loop.status.value,
                    _date_to_text(loop.due_on),
                    loop.priority,
                    loop.resolution_notes,
                    loop.created_at,
                    loop.updated_at,
                    loop.closed_at,
                ),
            )
        return loop

    def list_open_loops(
        self,
        person_id: str | None = None,
        *,
        status: OpenLoopStatus | None = None,
        overdue: bool = False,
    ) -> list[OpenLoop]:
        clauses: list[str] = []
        params: list[object] = []
        if person_id:
            clauses.append("person_id = ?")
            params.append(person_id)
        if status:
            clauses.append("status = ?")
            params.append(status.value)
        if overdue:
            clauses.append("due_on IS NOT NULL AND due_on < ? AND status IN ('open', 'deferred')")
            params.append(date.today().isoformat())
        sql = "SELECT * FROM open_loops"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY CASE WHEN due_on IS NULL THEN 1 ELSE 0 END, due_on, created_at DESC"
        rows = self.connection.execute(sql, params).fetchall()
        return [self.open_loop_from_row(row) for row in rows]

    def get_open_loop(self, loop_id: str) -> OpenLoop:
        row = self.connection.execute("SELECT * FROM open_loops WHERE id = ?", (loop_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"No open loop found for '{loop_id}'.")
        return self.open_loop_from_row(row)

    def update_open_loop(self, loop: OpenLoop) -> OpenLoop:
        loop.updated_at = now_iso()
        with self.connection:
            self.connection.execute(
                """
                UPDATE open_loops
                SET status = ?, due_on = ?, priority = ?, resolution_notes = ?, updated_at = ?, closed_at = ?
                WHERE id = ?
                """,
                (
                    loop.status.value,
                    _date_to_text(loop.due_on),
                    loop.priority,
                    loop.resolution_notes,
                    loop.updated_at,
                    loop.closed_at,
                    loop.id,
                ),
            )
        return loop

    def delete_open_loop(self, loop_id: str) -> None:
        self.get_open_loop(loop_id)
        with self.connection:
            self.connection.execute("DELETE FROM open_loops WHERE id = ?", (loop_id,))

    def add_suggestion(self, suggestion: SuggestedAction) -> SuggestedAction:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO suggested_actions (
                    id, person_id, open_loop_id, action_text, reason, priority_score, status, generated_at, acted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    action_text = excluded.action_text,
                    reason = excluded.reason,
                    priority_score = excluded.priority_score,
                    generated_at = excluded.generated_at
                WHERE suggested_actions.status = 'new'
                """,
                (
                    suggestion.id,
                    suggestion.person_id,
                    suggestion.open_loop_id,
                    suggestion.action_text,
                    suggestion.reason,
                    suggestion.priority_score,
                    suggestion.status.value,
                    suggestion.generated_at,
                    suggestion.acted_at,
                ),
            )
        return self.get_suggestion(suggestion.id)

    def list_suggestions(self, person_id: str | None = None, *, statuses: Iterable[SuggestionStatus] | None = None) -> list[SuggestedAction]:
        clauses: list[str] = []
        params: list[object] = []
        if person_id:
            clauses.append("person_id = ?")
            params.append(person_id)
        if statuses:
            status_values = [status.value for status in statuses]
            clauses.append(f"status IN ({','.join('?' for _ in status_values)})")
            params.extend(status_values)
        sql = "SELECT * FROM suggested_actions"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY priority_score DESC, generated_at DESC"
        rows = self.connection.execute(sql, params).fetchall()
        return [self.suggestion_from_row(row) for row in rows]

    def get_suggestion(self, suggestion_id: str) -> SuggestedAction:
        row = self.connection.execute("SELECT * FROM suggested_actions WHERE id = ?", (suggestion_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"No suggested action found for '{suggestion_id}'.")
        return self.suggestion_from_row(row)

    def update_suggestion(self, suggestion: SuggestedAction) -> SuggestedAction:
        with self.connection:
            self.connection.execute(
                "UPDATE suggested_actions SET status = ?, acted_at = ? WHERE id = ?",
                (suggestion.status.value, suggestion.acted_at, suggestion.id),
            )
        return suggestion

    def delete_suggestion(self, suggestion_id: str) -> None:
        self.get_suggestion(suggestion_id)
        with self.connection:
            self.connection.execute("DELETE FROM suggested_actions WHERE id = ?", (suggestion_id,))

    def add_person_note(self, note: RawNoteEntry) -> RawNoteEntry:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO person_notes (id, person_id, note, source, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (note.id, note.person_id, note.note, note.source, note.created_at),
            )
        return note

    def list_person_notes(self, person_id: str) -> list[RawNoteEntry]:
        rows = self.connection.execute(
            "SELECT * FROM person_notes WHERE person_id = ? ORDER BY created_at ASC, rowid ASC",
            (person_id,),
        ).fetchall()
        return [self.raw_note_from_row(row) for row in rows]

    def get_person_note(self, note_id: str) -> RawNoteEntry:
        row = self.connection.execute("SELECT * FROM person_notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"No raw note found for '{note_id}'.")
        return self.raw_note_from_row(row)

    def delete_person_note(self, note_id: str) -> None:
        self.get_person_note(note_id)
        with self.connection:
            self.connection.execute("DELETE FROM person_notes WHERE id = ?", (note_id,))

    def add_person_contact(self, contact: PersonContact) -> PersonContact:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO person_contacts (id, person_id, kind, label, value, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contact.id,
                    contact.person_id,
                    contact.kind,
                    contact.label,
                    contact.value,
                    contact.created_at,
                    contact.updated_at,
                ),
            )
            self.connection.execute(
                """
                INSERT OR IGNORE INTO contact_methods (
                    contact_method_id, person_id, type, label, value, normalized_value,
                    is_primary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    contact.id,
                    contact.person_id,
                    contact.kind,
                    contact.label,
                    contact.value,
                    contact.value.strip().lower(),
                    contact.created_at,
                    contact.updated_at,
                ),
            )
        return contact

    def list_person_contacts(self, person_id: str) -> list[PersonContact]:
        rows = self.connection.execute(
            "SELECT * FROM person_contacts WHERE person_id = ? ORDER BY kind, label, created_at",
            (person_id,),
        ).fetchall()
        return [self.contact_from_row(row) for row in rows]

    def get_person_contact(self, contact_id: str) -> PersonContact:
        row = self.connection.execute("SELECT * FROM person_contacts WHERE id = ?", (contact_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"No contact method found for '{contact_id}'.")
        return self.contact_from_row(row)

    def delete_person_contact(self, contact_id: str) -> None:
        self.get_person_contact(contact_id)
        with self.connection:
            self.connection.execute("DELETE FROM person_contacts WHERE id = ?", (contact_id,))
            self.connection.execute(
                "UPDATE contact_methods SET archived_at = ?, updated_at = ? WHERE contact_method_id = ?",
                (now_iso(), now_iso(), contact_id),
            )

    def add_evaluation(self, evaluation: Evaluation) -> Evaluation:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO evaluations (
                    id, person_id, suggested_action_id, interaction_id, outcome, impact_notes, evaluated_on, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation.id,
                    evaluation.person_id,
                    evaluation.suggested_action_id,
                    evaluation.interaction_id,
                    evaluation.outcome.value,
                    evaluation.impact_notes,
                    _date_to_text(evaluation.evaluated_on),
                    evaluation.created_at,
                ),
            )
        return evaluation

    def list_evaluations(self, person_id: str | None = None) -> list[Evaluation]:
        sql = "SELECT * FROM evaluations"
        params: list[object] = []
        if person_id:
            sql += " WHERE person_id = ?"
            params.append(person_id)
        sql += " ORDER BY evaluated_on DESC, created_at DESC"
        rows = self.connection.execute(sql, params).fetchall()
        return [self.evaluation_from_row(row) for row in rows]

    def dashboard_summary(self) -> DashboardSummary:
        today = date.today()
        due_soon = today + timedelta(days=7)
        total_people = self.connection.execute("SELECT COUNT(*) AS c FROM people").fetchone()["c"]
        recent_cutoff = (today - timedelta(days=30)).isoformat()
        recent = self.connection.execute(
            "SELECT COUNT(*) AS c FROM interactions WHERE occurred_on >= ?", (recent_cutoff,)
        ).fetchone()["c"]
        open_count = self.connection.execute(
            "SELECT COUNT(*) AS c FROM open_loops WHERE status IN ('open', 'deferred')"
        ).fetchone()["c"]
        overdue = self.connection.execute(
            "SELECT COUNT(*) AS c FROM open_loops WHERE status IN ('open', 'deferred') AND due_on IS NOT NULL AND due_on < ?",
            (today.isoformat(),),
        ).fetchone()["c"]
        soon = self.connection.execute(
            "SELECT COUNT(*) AS c FROM open_loops WHERE status IN ('open', 'deferred') AND due_on BETWEEN ? AND ?",
            (today.isoformat(), due_soon.isoformat()),
        ).fetchone()["c"]
        return DashboardSummary(
            total_people=total_people,
            recent_interactions=recent,
            open_loops=open_count,
            overdue_followups=overdue,
            due_soon_followups=soon,
            top_suggestions=self.list_suggestions(statuses=[SuggestionStatus.NEW])[:5],
        )

    def dossier(self, person_id: str) -> Dossier:
        person = self.get_person(person_id)
        interactions = self.list_interactions(person_id, limit=10)
        return Dossier(
            person=person,
            v1_person=self.get_v1_person(person_id),
            contacts=self.list_person_contacts(person_id),
            contact_methods=self.list_contact_methods(person_id),
            relationships=self.list_relationships(person_id),
            v1_interactions=self.list_v1_interactions_for_person(person_id),
            signals_v1=self.list_signals(person_id),
            opportunities=self.list_opportunities_for_person(person_id),
            relationship_links=self.list_relationship_links_for_entity("person", person_id),
            open_loops=self.list_open_loops(person_id),
            recent_interactions=interactions,
            suggestions=self.list_suggestions(person_id),
            evaluations=self.list_evaluations(person_id),
            raw_notes=self.list_person_notes(person_id),
            last_contact=interactions[0].occurred_on if interactions else None,
        )

    def timeline(self, person_id: str | None = None) -> list[TimelineEntry]:
        entries = []
        for interaction in self.list_interactions(person_id):
            loops = [
                loop
                for loop in self.list_open_loops(interaction.person_id)
                if loop.source_interaction_id == interaction.id
            ]
            evaluations = [
                evaluation
                for evaluation in self.list_evaluations(interaction.person_id)
                if evaluation.interaction_id == interaction.id
            ]
            entries.append(TimelineEntry(interaction=interaction, open_loops=loops, evaluations=evaluations))
        return entries
