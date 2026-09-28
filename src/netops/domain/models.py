from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from netops.domain.validation import normalize_text_list
from netops.domain.validation import (
    normalize_bool_flag,
    normalize_date_text,
    normalize_multiline_text,
    normalize_optional_text,
    normalize_required_text,
    require_entity_type,
)


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
        return normalize_optional_text(value)


class V1Person(NetOpsModel):
    person_id: str = Field(default_factory=new_id)
    name: str
    alias: str | None = None
    role: str | None = None
    organization: str | None = None
    location: str | None = None
    birthday: str | None = None
    profile_photo_path: str | None = None
    relationship_type: str | None = None
    relationship_status: str | None = None
    relationship_strength: str | None = None
    origin_story: str | None = None
    importance_reason: str | None = None
    dossier: str | None = None
    interests: str | None = None
    communication_style: str | None = None
    preferences: str | None = None
    current_goals: str | None = None
    potential_value: str | None = None
    first_met: str | None = None
    last_contact: str | None = None
    next_action: str | None = None
    follow_up_date: str | None = None
    follow_up_completed_at: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    archived_at: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def name_required(cls, value: object) -> str:
        return normalize_required_text(value, "Name")

    @field_validator("origin_story", "importance_reason", "dossier", "interests", "communication_style", "preferences", "current_goals", "potential_value", mode="before")
    @classmethod
    def preserve_long_text(cls, value: object) -> str | None:
        return normalize_multiline_text(value)

    @field_validator("birthday", "first_met", "last_contact", "follow_up_date", mode="before")
    @classmethod
    def validate_dates(cls, value: object) -> str | None:
        return normalize_date_text(value, allow_month=True)

    @field_validator("relationship_strength", mode="before")
    @classmethod
    def v1_strength_text(cls, value: object) -> str | None:
        return normalize_optional_text(value)


class ContactMethod(NetOpsModel):
    contact_method_id: str = Field(default_factory=new_id)
    person_id: str
    type: str
    label: str | None = None
    value: str
    normalized_value: str | None = None
    is_primary: int = 0
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    archived_at: str | None = None

    @field_validator("person_id", "type", "value", mode="before")
    @classmethod
    def required_contact_text(cls, value: object) -> str:
        return normalize_required_text(value, "Contact value")

    @field_validator("type", mode="after")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("is_primary", mode="before")
    @classmethod
    def normalize_primary(cls, value: object) -> int:
        return normalize_bool_flag(value)


class V1Interaction(NetOpsModel):
    interaction_id: str = Field(default_factory=new_id)
    interaction_date: str = Field(default_factory=lambda: date.today().isoformat())
    interaction_type: str | None = None
    summary: str | None = None
    takeaways: str | None = None
    action_items: str | None = None
    sentiment: str | None = None
    follow_up_required: int = 0
    follow_up_date: str | None = None
    follow_up_completed_at: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    archived_at: str | None = None

    @field_validator("interaction_date", "follow_up_date", mode="before")
    @classmethod
    def validate_interaction_dates(cls, value: object) -> str | None:
        return normalize_date_text(value)

    @field_validator("summary", "takeaways", "action_items", mode="before")
    @classmethod
    def preserve_interaction_text(cls, value: object) -> str | None:
        return normalize_multiline_text(value)

    @field_validator("follow_up_required", mode="before")
    @classmethod
    def normalize_follow_flag(cls, value: object) -> int:
        return normalize_bool_flag(value)


class InteractionPerson(NetOpsModel):
    interaction_person_id: str = Field(default_factory=new_id)
    interaction_id: str
    person_id: str
    role: str | None = None
    is_primary: int = 0
    created_at: str = Field(default_factory=now_iso)

    @field_validator("interaction_id", "person_id", mode="before")
    @classmethod
    def required_link_text(cls, value: object) -> str:
        return normalize_required_text(value, "Link value")

    @field_validator("is_primary", mode="before")
    @classmethod
    def normalize_link_primary(cls, value: object) -> int:
        return normalize_bool_flag(value)


class Signal(NetOpsModel):
    signal_id: str = Field(default_factory=new_id)
    person_id: str
    signal_text: str
    confidence: str | None = None
    source_interaction_id: str | None = None
    source_description: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    archived_at: str | None = None

    @field_validator("person_id", mode="before")
    @classmethod
    def required_signal_person(cls, value: object) -> str:
        return normalize_required_text(value, "Person")

    @field_validator("signal_text", mode="before")
    @classmethod
    def required_signal_text(cls, value: object) -> str:
        return normalize_required_text(value, "Signal text")


class Opportunity(NetOpsModel):
    opportunity_id: str = Field(default_factory=new_id)
    title: str
    status: str = "open"
    description: str | None = None
    follow_up_date: str | None = None
    follow_up_completed_at: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    closed_at: str | None = None
    archived_at: str | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def required_opportunity_text(cls, value: object) -> str:
        return normalize_required_text(value, "Opportunity value")

    @field_validator("description", mode="before")
    @classmethod
    def preserve_opportunity_text(cls, value: object) -> str | None:
        return normalize_multiline_text(value)

    @field_validator("follow_up_date", mode="before")
    @classmethod
    def validate_opportunity_date(cls, value: object) -> str | None:
        return normalize_date_text(value)


class OpportunityPerson(NetOpsModel):
    opportunity_person_id: str = Field(default_factory=new_id)
    opportunity_id: str
    person_id: str
    role: str | None = None
    is_primary: int = 0
    created_at: str = Field(default_factory=now_iso)

    @field_validator("opportunity_id", "person_id", mode="before")
    @classmethod
    def required_opportunity_link_text(cls, value: object) -> str:
        return normalize_required_text(value, "Opportunity link value")

    @field_validator("is_primary", mode="before")
    @classmethod
    def normalize_opportunity_primary(cls, value: object) -> int:
        return normalize_bool_flag(value)


class RelationshipLink(NetOpsModel):
    relationship_link_id: str = Field(default_factory=new_id)
    source_entity_type: str
    source_entity_id: str
    target_entity_type: str
    target_entity_id: str
    relationship_type: str
    description: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    archived_at: str | None = None

    @field_validator("source_entity_type", "target_entity_type", mode="before")
    @classmethod
    def validate_entity_type(cls, value: str) -> str:
        return require_entity_type(value)

    @field_validator("source_entity_id", "target_entity_id", "relationship_type", mode="before")
    @classmethod
    def required_relationship_link_text(cls, value: object) -> str:
        return normalize_required_text(value, "Relationship link value")

    @field_validator("description", mode="before")
    @classmethod
    def preserve_link_description(cls, value: object) -> str | None:
        return normalize_multiline_text(value)


class Tag(NetOpsModel):
    tag_id: str = Field(default_factory=new_id)
    name: str
    normalized_name: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    archived_at: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def required_tag_name(cls, value: object) -> str:
        return normalize_required_text(value, "Tag name")

    @model_validator(mode="after")
    def fill_normalized_name(self) -> "Tag":
        if not self.normalized_name:
            self.normalized_name = self.name.strip().lower()
        return self


class Tagging(NetOpsModel):
    tagging_id: str = Field(default_factory=new_id)
    tag_id: str
    entity_type: str
    entity_id: str
    created_at: str = Field(default_factory=now_iso)

    @field_validator("tag_id", "entity_id", mode="before")
    @classmethod
    def required_tagging_text(cls, value: object) -> str:
        return normalize_required_text(value, "Tagging value")

    @field_validator("entity_type", mode="before")
    @classmethod
    def validate_tagging_type(cls, value: str) -> str:
        return require_entity_type(value)


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


class PersonContact(NetOpsModel):
    id: str = Field(default_factory=new_id)
    person_id: str
    kind: str
    label: str | None = None
    value: str
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)

    @field_validator("person_id", "kind", "value")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Required contact value is missing.")
        return value


class TimelineEntry(NetOpsModel):
    interaction: Interaction
    open_loops: list[OpenLoop] = Field(default_factory=list)
    evaluations: list[Evaluation] = Field(default_factory=list)


class Dossier(NetOpsModel):
    person: Person
    v1_person: V1Person | None = None
    contacts: list[PersonContact] = Field(default_factory=list)
    contact_methods: list[ContactMethod] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    v1_interactions: list[V1Interaction] = Field(default_factory=list)
    signals_v1: list[Signal] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    relationship_links: list[RelationshipLink] = Field(default_factory=list)
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
