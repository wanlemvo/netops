from __future__ import annotations

from datetime import date

from netops.domain.models import Interaction, OpenLoop
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

