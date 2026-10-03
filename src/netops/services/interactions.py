from __future__ import annotations

from datetime import date

from netops.domain.models import Interaction, InteractionPerson, OpenLoop, V1Interaction
from netops.domain.validation import require_not_future
from netops.storage.repositories import NetOpsRepository


class InteractionService:
    def __init__(self, repository: NetOpsRepository, people_service) -> None:
        self.repository = repository
        self.people_service = people_service

    def log_interaction(
        self,
        person_query: str,
        *,
        occurred_on: date,
        interaction_type: str,
        notes: str,
        follow_up: str | None = None,
        due_on: date | None = None,
        allow_future: bool = False,
    ) -> tuple[Interaction, OpenLoop | None]:
        require_not_future(occurred_on, allow_future=allow_future)
        person = self.people_service.resolve_person(person_query)
        interaction = self.repository.add_interaction(
            Interaction(
                person_id=person.id,
                occurred_on=occurred_on,
                interaction_type=interaction_type,
                notes=notes,
            )
        )
        loop = None
        if follow_up:
            loop = self.repository.add_open_loop(
                OpenLoop(
                    person_id=person.id,
                    source_interaction_id=interaction.id,
                    description=follow_up,
                    due_on=due_on,
                )
            )
        return interaction, loop

    def timeline(self, person_query: str | None = None):
        if person_query:
            person = self.people_service.resolve_person(person_query)
            return self.repository.timeline(person.id)
        return self.repository.timeline()

    def log_v1_interaction(
        self,
        person_queries: list[str],
        *,
        interaction_date: str,
        interaction_type: str | None = None,
        summary: str | None = None,
        takeaways: str | None = None,
        action_items: str | None = None,
        sentiment: str | None = None,
        follow_up_required: bool = False,
        follow_up_date: str | None = None,
    ) -> V1Interaction:
        if not person_queries:
            raise ValueError("At least one person is required.")
        people = [self.people_service.resolve_person(query) for query in person_queries]
        interaction = V1Interaction(
            interaction_date=interaction_date,
            interaction_type=interaction_type,
            summary=summary,
            takeaways=takeaways,
            action_items=action_items,
            sentiment=sentiment,
            follow_up_required=1 if follow_up_required or (follow_up_date and follow_up_date.strip()) else 0,
            follow_up_date=follow_up_date,
        )
        participants = [
            InteractionPerson(
                interaction_id=interaction.interaction_id,
                person_id=person.id,
                role="primary" if index == 0 else "participant",
                is_primary=1 if index == 0 else 0,
            )
            for index, person in enumerate(people)
        ]
        return self.repository.add_v1_interaction(interaction, participants)

    def list_v1_interactions(self, person_query: str) -> list[V1Interaction]:
        person = self.people_service.resolve_person(person_query)
        return self.repository.list_v1_interactions_for_person(person.id)
