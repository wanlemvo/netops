from __future__ import annotations

from datetime import date
from typing import Any

from netops.domain.models import (
    ContactMethod,
    Opportunity,
    Person,
    RelationshipLink,
    Signal,
    V1Interaction,
    V1Person,
)
from netops.domain.validation import NotFoundError, UserInputError
from netops.services.interactions import InteractionService
from netops.services.open_loops import OpenLoopService
from netops.services.people import PeopleService
from netops.storage import NetOpsRepository, connect

JsonDict = dict[str, Any]


PERSON_FIELDS = {
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

CONTACT_PAYLOAD_FIELDS = {
    "email": "email",
    "phone": "phone",
    "linkedin": "linkedin",
    "github": "github",
    "other_social": "social",
}


class NetworkOpsBackend:
    """GUI/application-facing facade over the local NetworkOps service layer.

    The terminal surfaces can stay focused on prompts and rendering while this
    class returns JSON-safe dictionaries shaped for future desktop/web views.
    """

    def __init__(self, repository: NetOpsRepository | None = None) -> None:
        self.repository = repository or NetOpsRepository(connect())
        self.people = PeopleService(self.repository)
        self.interactions = InteractionService(self.repository, self.people)
        self.loops = OpenLoopService(self.repository, self.people)

    def get_overview(self) -> JsonDict:
        people = self.repository.list_v1_people()
        follow_ups = self.review_followups()
        recent_intel = self._recent_intel(people)
        dormant_people = [
            person
            for person in people
            if not person.last_contact
            and not self.repository.list_v1_interactions_for_person(person.person_id)
            and not person.next_action
            and not person.follow_up_date
        ]

        return {
            "view": "overview",
            "system_state": {
                "files": len(people),
                "open_loops": len(follow_ups),
                "dormant": len(dormant_people),
            },
            "people": self.list_people(),
            "recent_intel": recent_intel[:10],
            "follow_ups": follow_ups[:10],
            "dormant_people": [self._person_list_item(person) for person in dormant_people[:10]],
        }

    def list_people(self, *, search: str | None = None, tag: str | None = None) -> list[JsonDict]:
        rows: list[JsonDict] = []
        search_text = search.strip().lower() if search else ""
        tag_text = tag.strip().lower() if tag else ""

        for person in self.repository.list_v1_people():
            legacy = self._legacy_person(person.person_id)
            tags = legacy.tags if legacy else []
            haystack = " ".join(
                value
                for value in [
                    person.name,
                    person.alias or "",
                    person.role or "",
                    person.organization or "",
                    person.location or "",
                    " ".join(tags),
                ]
                if value
            ).lower()
            if search_text and search_text not in haystack:
                continue
            if tag_text and tag_text not in {candidate.lower() for candidate in tags}:
                continue
            rows.append(self._person_list_item(person, tags=tags))
        return rows

    def get_person(self, person_query: str) -> JsonDict:
        person = self.people.get_v1_person(person_query)
        legacy = self._legacy_person(person.person_id)
        return self._person_detail(person, tags=legacy.tags if legacy else [])

    def get_dossier(self, person_query: str) -> JsonDict:
        dossier = self.people.dossier(person_query)
        person = dossier.v1_person or self.people.get_v1_person(dossier.person.id)
        legacy = dossier.person
        contacts = [self._contact_method_item(contact) for contact in dossier.contact_methods]
        relationship_links = [self._relationship_link_item(link, focus_person_id=person.person_id) for link in dossier.relationship_links]
        interactions = [self._interaction_item(interaction, person=person) for interaction in dossier.v1_interactions]
        signals = [self._signal_item(signal, person=person) for signal in dossier.signals_v1]
        opportunities = [self._opportunity_item(opportunity, person=person) for opportunity in dossier.opportunities]
        open_loops = [loop.model_dump(mode="json") for loop in dossier.open_loops]
        raw_notes = [note.model_dump(mode="json") for note in dossier.raw_notes]

        current_read = self._first_text(
            person.dossier,
            person.importance_reason,
            person.potential_value,
            person.origin_story,
            fallback="No current read recorded.",
        )
        timeline = [*interactions, *signals]
        timeline.sort(key=lambda item: item.get("sort_date") or "", reverse=True)

        return {
            "view": "dossier",
            "person": self._person_detail(person, tags=legacy.tags),
            "header": {
                "title": person.name,
                "subtitle": self._subtitle(person),
                "profile_photo_path": person.profile_photo_path,
                "rule": "Only logged, shared, observed, or publicly known info.",
            },
            "current_read": current_read,
            "summary_cards": [
                {
                    "id": "relationship_status",
                    "label": "Relationship Status",
                    "value": self._first_text(person.relationship_status, person.relationship_strength),
                },
                {
                    "id": "strategic_value",
                    "label": "Strategic Value",
                    "value": self._first_text(person.potential_value, person.importance_reason),
                },
                {
                    "id": "best_move",
                    "label": "Best Move",
                    "value": self._first_text(person.next_action, self._first_follow_up_action(person.person_id)),
                },
            ],
            "identity_records": {
                "known_as": self._known_as(person),
                "location": person.location,
                "category": person.relationship_type,
                "tags": legacy.tags,
            },
            "contact_records": {
                "preferred": self._preferred_contact(contacts),
                "methods": contacts,
                "response_style": person.communication_style,
            },
            "known_profile": {
                "skills": person.interests,
                "interests": person.interests,
                "communication": person.communication_style,
                "preferences": person.preferences,
                "constraints": person.current_goals,
            },
            "connections": relationship_links,
            "intel_timeline": timeline,
            "raw_notes_vault": raw_notes,
            "dossier_folders": [
                {"id": "identity", "label": "Full Identity File", "count": 1},
                {"id": "contacts", "label": "All Contact Methods", "count": len(contacts)},
                {"id": "interactions", "label": "Interaction Archive", "count": len(interactions)},
                {"id": "signals", "label": "Signal Ledger", "count": len(signals)},
                {"id": "opportunities", "label": "Opportunity Map", "count": len(opportunities)},
                {"id": "connections", "label": "Relationship Links", "count": len(relationship_links)},
            ],
            "folder_payloads": {
                "identity": self._person_detail(person, tags=legacy.tags),
                "contacts": contacts,
                "interactions": interactions,
                "signals": signals,
                "opportunities": opportunities,
                "connections": relationship_links,
                "open_loops": open_loops,
                "legacy_raw_notes": raw_notes,
            },
            "actions": [
                "edit_person",
                "add_contact_method",
                "log_interaction",
                "add_signal",
                "add_opportunity",
                "add_relationship_link",
                "set_profile_photo",
            ],
        }

    def create_person(self, payload: JsonDict) -> JsonDict:
        kwargs = self._person_kwargs(payload, require_name=True)
        person = self.people.create_v1_person(**kwargs)
        self._create_inline_contact_methods(person.person_id, payload)
        return self.get_person(person.person_id)

    def update_person(self, person_query: str, payload: JsonDict) -> JsonDict:
        person_fields = self._person_kwargs(payload, require_name=False)
        person_fields.pop("tags", None)
        for key, value in person_fields.items():
            self.people.update_v1_person_field(person_query, key, value)
        if "tags" in payload:
            legacy = self.people.resolve_person(person_query)
            legacy.tags = self._text_list(payload.get("tags"))
            self.repository.update_person(legacy)
        self._create_inline_contact_methods(person_query, payload)
        return self.get_person(person_query)

    def add_contact_method(self, person_query: str, payload: JsonDict) -> JsonDict:
        contact = self.people.add_contact_method(
            person_query,
            kind=str(payload.get("type") or payload.get("kind") or "other"),
            label=payload.get("label"),
            value=str(payload.get("value") or ""),
            is_primary=bool(payload.get("is_primary", False)),
        )
        return self._contact_method_item(contact)

    def add_interaction(self, payload: JsonDict) -> JsonDict:
        people = self._people_from_payload(payload)
        interaction = self.interactions.log_v1_interaction(
            people,
            interaction_date=str(payload.get("interaction_date") or payload.get("date") or date.today().isoformat()),
            interaction_type=payload.get("interaction_type") or payload.get("type"),
            summary=payload.get("summary"),
            takeaways=payload.get("takeaways"),
            action_items=payload.get("action_items"),
            sentiment=payload.get("sentiment"),
            follow_up_required=bool(payload.get("follow_up_required", False)),
            follow_up_date=payload.get("follow_up_date"),
        )
        return interaction.model_dump(mode="json")

    def add_signal(self, person_query: str, payload: JsonDict) -> JsonDict:
        signal = self.people.add_signal(
            person_query,
            text=str(payload.get("signal_text") or payload.get("text") or ""),
            confidence=payload.get("confidence"),
            source_interaction_id=payload.get("source_interaction_id"),
            source_description=payload.get("source_description") or payload.get("source"),
        )
        return self._signal_item(signal, person=self.people.get_v1_person(person_query))

    def add_opportunity(self, payload: JsonDict) -> JsonDict:
        people = self._people_from_payload(payload)
        opportunity = self.people.add_opportunity(
            people,
            title=str(payload.get("title") or ""),
            status=str(payload.get("status") or "open"),
            description=payload.get("description"),
            follow_up_date=payload.get("follow_up_date"),
        )
        primary_person = self.people.get_v1_person(people[0])
        return self._opportunity_item(opportunity, person=primary_person)

    def add_relationship_link(self, payload: JsonDict) -> JsonDict:
        source = str(payload.get("source_person_id") or payload.get("source") or "")
        target = str(payload.get("target_person_id") or payload.get("target") or "")
        link = self.people.add_relationship_link(
            source,
            target,
            relationship_type=str(payload.get("relationship_type") or payload.get("type") or ""),
            description=payload.get("description"),
        )
        source_person = self.people.resolve_person(source)
        return self._relationship_link_item(link, focus_person_id=source_person.id)

    def review_followups(self) -> list[JsonDict]:
        return [dict(row) for row in self.loops.review_v1_follow_ups()]

    def _person_kwargs(self, payload: JsonDict, *, require_name: bool) -> JsonDict:
        kwargs = {key: payload[key] for key in PERSON_FIELDS if key in payload}
        if require_name and not str(kwargs.get("name") or "").strip():
            raise UserInputError("Name is required.")
        if "tags" in payload:
            kwargs["tags"] = self._text_list(payload["tags"])
        return kwargs

    def _create_inline_contact_methods(self, person_query: str, payload: JsonDict) -> None:
        for field, contact_type in CONTACT_PAYLOAD_FIELDS.items():
            value = str(payload.get(field) or "").strip()
            if value:
                self.people.add_contact_method(
                    person_query,
                    kind=contact_type,
                    label=field,
                    value=value,
                    is_primary=contact_type in {"email", "phone"},
                )
        for contact in payload.get("contact_methods") or []:
            if isinstance(contact, dict) and str(contact.get("value") or "").strip():
                self.add_contact_method(person_query, contact)

    def _people_from_payload(self, payload: JsonDict) -> list[str]:
        people = payload.get("people") or payload.get("person_ids") or payload.get("person_queries")
        if isinstance(people, str):
            return [people]
        if not people:
            person = payload.get("person_id") or payload.get("person")
            people = [person] if person else []
        result = [str(person).strip() for person in people if str(person).strip()]
        if not result:
            raise UserInputError("At least one person is required.")
        return result

    def _recent_intel(self, people: list[V1Person]) -> list[JsonDict]:
        items: list[JsonDict] = []
        for person in people:
            interactions = self.repository.list_v1_interactions_for_person(person.person_id)[:3]
            signals = self.repository.list_signals(person.person_id)[:3]
            items.extend(self._interaction_item(interaction, person=person) for interaction in interactions)
            items.extend(self._signal_item(signal, person=person) for signal in signals)
        items.sort(key=lambda item: item.get("sort_date") or "", reverse=True)
        return items

    def _person_list_item(self, person: V1Person, *, tags: list[str] | None = None) -> JsonDict:
        return {
            "person_id": person.person_id,
            "name": person.name,
            "alias": person.alias,
            "role": person.role,
            "organization": person.organization,
            "location": person.location,
            "relationship_type": person.relationship_type,
            "relationship_status": person.relationship_status,
            "relationship_strength": person.relationship_strength,
            "next_action": person.next_action,
            "follow_up_date": person.follow_up_date,
            "profile_photo_path": person.profile_photo_path,
            "tags": tags if tags is not None else self._tags_for_person(person.person_id),
        }

    def _person_detail(self, person: V1Person, *, tags: list[str]) -> JsonDict:
        data = person.model_dump(mode="json")
        data["tags"] = tags
        data["subtitle"] = self._subtitle(person)
        return data

    def _interaction_item(self, interaction: V1Interaction, *, person: V1Person) -> JsonDict:
        return {
            "kind": "interaction",
            "person_id": person.person_id,
            "person": person.name,
            "id": interaction.interaction_id,
            "date": interaction.interaction_date,
            "sort_date": interaction.interaction_date,
            "title": interaction.interaction_type or "interaction",
            "summary": interaction.summary,
            "takeaways": interaction.takeaways,
            "action_items": interaction.action_items,
            "sentiment": interaction.sentiment,
            "follow_up_required": bool(interaction.follow_up_required),
            "follow_up_date": interaction.follow_up_date,
        }

    def _signal_item(self, signal: Signal, *, person: V1Person) -> JsonDict:
        return {
            "kind": "signal",
            "person_id": person.person_id,
            "person": person.name,
            "id": signal.signal_id,
            "date": signal.created_at[:10],
            "sort_date": signal.created_at,
            "title": "signal",
            "text": signal.signal_text,
            "confidence": signal.confidence,
            "source_interaction_id": signal.source_interaction_id,
            "source_description": signal.source_description,
        }

    def _opportunity_item(self, opportunity: Opportunity, *, person: V1Person) -> JsonDict:
        return {
            "kind": "opportunity",
            "person_id": person.person_id,
            "person": person.name,
            "id": opportunity.opportunity_id,
            "title": opportunity.title,
            "status": opportunity.status,
            "description": opportunity.description,
            "follow_up_date": opportunity.follow_up_date,
            "created_at": opportunity.created_at,
            "updated_at": opportunity.updated_at,
        }

    def _relationship_link_item(self, link: RelationshipLink, *, focus_person_id: str) -> JsonDict:
        other_type, other_id = (
            (link.target_entity_type, link.target_entity_id)
            if link.source_entity_id == focus_person_id
            else (link.source_entity_type, link.source_entity_id)
        )
        return {
            "kind": "relationship_link",
            "id": link.relationship_link_id,
            "source_entity_type": link.source_entity_type,
            "source_entity_id": link.source_entity_id,
            "target_entity_type": link.target_entity_type,
            "target_entity_id": link.target_entity_id,
            "relationship_type": link.relationship_type,
            "description": link.description,
            "other_entity_type": other_type,
            "other_entity_id": other_id,
            "other_entity_label": self._entity_label(other_type, other_id),
            "created_at": link.created_at,
            "updated_at": link.updated_at,
        }

    def _contact_method_item(self, contact: ContactMethod | JsonDict) -> JsonDict:
        if isinstance(contact, dict):
            return contact
        return contact.model_dump(mode="json")

    def _legacy_person(self, person_id: str) -> Person | None:
        try:
            return self.repository.get_person(person_id)
        except NotFoundError:
            return None

    def _tags_for_person(self, person_id: str) -> list[str]:
        legacy = self._legacy_person(person_id)
        return legacy.tags if legacy else []

    def _entity_label(self, entity_type: str, entity_id: str) -> str:
        if entity_type != "person":
            return entity_id
        try:
            return self.repository.get_v1_person(entity_id).name
        except NotFoundError:
            return entity_id

    def _subtitle(self, person: V1Person) -> str:
        parts = [person.role, person.organization, person.location]
        return " // ".join(part for part in parts if part) or "Person Intelligence Record"

    def _known_as(self, person: V1Person) -> str:
        names = [person.name, person.alias]
        return ", ".join(name for name in names if name)

    def _preferred_contact(self, contacts: list[JsonDict]) -> JsonDict | None:
        if not contacts:
            return None
        primary = [contact for contact in contacts if contact.get("is_primary")]
        return primary[0] if primary else contacts[0]

    def _first_follow_up_action(self, person_id: str) -> str | None:
        for follow_up in self.review_followups():
            if follow_up.get("id") == person_id:
                return follow_up.get("action") or follow_up.get("title")
        return None

    def _first_text(self, *values: object, fallback: str = "unset") -> str:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return fallback

    def _text_list(self, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value).strip()] if str(value).strip() else []
