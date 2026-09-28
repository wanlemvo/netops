from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from netops.domain.validation import normalize_relationship_strength, normalize_text_list


def new_id() -> str:
    return uuid4().hex


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


class NetOpsModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


class InteractionType(StrEnum):
    CALL = "call"
    MESSAGE = "message"
    MEETING = "meeting"
    EMAIL = "email"
    NOTE = "note"
    CUSTOM = "custom"


class OpenLoopStatus(StrEnum):
    OPEN = "open"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    CLOSED_NO_ACTION = "closed_no_action"


class SuggestionStatus(StrEnum):
    NEW = "new"
    ACCEPTED = "accepted"
    IGNORED = "ignored"
    COMPLETED = "completed"


class EvaluationOutcome(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class Person(NetOpsModel):
    id: str = Field(default_factory=new_id)
    display_name: str
    given_name: str | None = None
    family_name: str | None = None
    primary_email: str | None = None
    primary_phone: str | None = None
    organization: str | None = None
    tags: list[str] = Field(default_factory=list)
    relationship_notes: str | None = None
    alias: str | None = None
    role: str | None = None
    location: str | None = None
    relationship_type: str | None = None
    relationship_strength: str | None = None
    birthday: str | None = None
    interests: list[str] = Field(default_factory=list)
    communication_style: str | None = None
    preferences_notes: str | None = None
    signals: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

    @field_validator("display_name")
    @classmethod
    def display_name_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Person name is required.")
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> list[str]:
        return normalize_text_list(value)

    @field_validator("interests", "signals", mode="before")
    @classmethod
    def normalize_profile_lists(cls, value: Any) -> list[str]:
        return normalize_text_list(value)

    @field_validator("relationship_strength", mode="before")
    @classmethod
    def normalize_strength(cls, value: Any) -> str | None:
        return normalize_relationship_strength(value)


class Relationship(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    related_person_id: str | None = None
    relationship_type: str
    strength: str | None = None
    notes: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

    @field_validator("person_id", "relationship_type")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Required relationship value is missing.")
        return value

    @model_validator(mode="after")
    def no_self_relationship(self) -> "Relationship":
        if self.related_person_id and self.related_person_id == self.person_id:
            raise ValueError("A person cannot be related to themselves.")
        return self


class Interaction(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    occurred_on: date = Field(default_factory=date.today)
    interaction_type: str
    notes: str
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

    @field_validator("person_id", "interaction_type", "notes")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Required interaction value is missing.")
        return value


class OpenLoop(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    source_interaction_id: str | None = None
    description: str
    status: OpenLoopStatus = OpenLoopStatus.OPEN
    due_on: date | None = None
    priority: int | None = None
    resolution_notes: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    closed_at: str | None = None

    @field_validator("person_id", "description")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Required open-loop value is missing.")
        return value

    @model_validator(mode="after")
    def closed_states_have_timestamp(self) -> "OpenLoop":
        if self.status in {OpenLoopStatus.COMPLETED, OpenLoopStatus.CLOSED_NO_ACTION} and not self.closed_at:
            self.closed_at = now_iso()
        return self


class SuggestedAction(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    open_loop_id: str | None = None
    action_text: str
    reason: str
    priority_score: int
    status: SuggestionStatus = SuggestionStatus.NEW
    generated_at: str = Field(default_factory=now_iso)
    acted_at: str | None = None

    @field_validator("person_id", "action_text", "reason")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Required suggestion value is missing.")
        return value


class Evaluation(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    suggested_action_id: str | None = None
    interaction_id: str | None = None
    outcome: EvaluationOutcome
    impact_notes: str | None = None
    evaluated_on: date = Field(default_factory=date.today)
    created_at: str = Field(default_factory=now_iso)


class RawNoteEntry(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    note: str
    source: str | None = "dossier"
    created_at: str = Field(default_factory=now_iso)

    @field_validator("person_id", "note")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Required raw note value is missing.")
        return value

class TimelineEntry(NetOpsModel):
    interaction: Interaction
    open_loops: list[OpenLoop] = Field(default_factory=list)
    evaluations: list[Evaluation] = Field(default_factory=list)


class Dossier(NetOpsModel):
    person: Person
    relationships: list[Relationship] = Field(default_factory=list)
    open_loops: list[OpenLoop] = Field(default_factory=list)
    recent_interactions: list[Interaction] = Field(default_factory=list)
    suggestions: list[SuggestedAction] = Field(default_factory=list)
    evaluations: list[Evaluation] = Field(default_factory=list)
    raw_notes: list[RawNoteEntry] = Field(default_factory=list)
    last_contact: date | None = None


class DashboardSummary(NetOpsModel):
    total_people: int = 0
    recent_interactions: int = 0
    open_loops: int = 0
    overdue_followups: int = 0
    due_soon_followups: int = 0
    top_suggestions: list[SuggestedAction] = Field(default_factory=list)
