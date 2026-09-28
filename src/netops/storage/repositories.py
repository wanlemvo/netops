from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from typing import Iterable

from netops.domain.models import (
    DashboardSummary,
    Dossier,
    Evaluation,
    EvaluationOutcome,
    Interaction,
    OpenLoop,
    OpenLoopStatus,
    Person,
    RawNoteEntry,
    Relationship,
    SuggestedAction,
    SuggestionStatus,
    TimelineEntry,
    now_iso,
)
from netops.domain.validation import NotFoundError
from netops.storage.migrations import migrate


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _date_from_text(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


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


class NetOpsRepository:
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
        return person

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
                INSERT INTO interactions (id, person_id, occurred_on, interaction_type, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction.id,
                    interaction.person_id,
                    _date_to_text(interaction.occurred_on),
                    interaction.interaction_type,
                    interaction.notes,
                    interaction.created_at,
                    interaction.updated_at,
                ),
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

    def add_suggestion(self, suggestion: SuggestedAction) -> SuggestedAction:
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO suggested_actions (
                    id, person_id, open_loop_id, action_text, reason, priority_score, status, generated_at, acted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        return suggestion

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
            relationships=self.list_relationships(person_id),
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
