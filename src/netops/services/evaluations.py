from __future__ import annotations

from datetime import date

from netops.domain.models import Evaluation, EvaluationOutcome
from netops.storage.repositories import NetOpsRepository


class EvaluationService:
    def __init__(self, repository: NetOpsRepository, people_service) -> None:
        self.repository = repository
        self.people_service = people_service

    def create(
        self,
        *,
        person_query: str | None,
        suggested_action_id: str | None = None,
        interaction_id: str | None = None,
        outcome: str,
        notes: str | None = None,
        evaluated_on: date | None = None,
    ) -> Evaluation:
        if person_query:
            person_id = self.people_service.resolve_person(person_query).id
        elif suggested_action_id:
            person_id = self.repository.get_suggestion(suggested_action_id).person_id
        elif interaction_id:
            person_id = self.repository.get_interaction(interaction_id).person_id
        else:
            raise ValueError("Evaluation requires a person, action, or interaction.")
        return self.repository.add_evaluation(
            Evaluation(
                person_id=person_id,
                suggested_action_id=suggested_action_id,
                interaction_id=interaction_id,
                outcome=EvaluationOutcome(outcome),
                impact_notes=notes,
                evaluated_on=evaluated_on or date.today(),
            )
        )

    def list_for_person(self, person_query: str):
        person = self.people_service.resolve_person(person_query)
        return self.repository.list_evaluations(person.id)

