from __future__ import annotations

from netops.domain.models import SuggestedAction, SuggestionStatus, now_iso
from netops.domain.suggestions import generate_suggestions
from netops.storage.repositories import NetOpsRepository


class SuggestionService:
    def __init__(self, repository: NetOpsRepository, people_service) -> None:
        self.repository = repository
        self.people_service = people_service

    def generate(
        self,
        *,
        person_query: str | None = None,
        limit: int = 10,
        include_low_priority: bool = False,
    ) -> list[SuggestedAction]:
        person_id = self.people_service.resolve_person(person_query).id if person_query else None
        suggestions = generate_suggestions(self.repository, person_id=person_id)
        if not include_low_priority:
            suggestions = [suggestion for suggestion in suggestions if suggestion.priority_score >= 30]
        return suggestions[:limit]

    def save_action(self, suggestion: SuggestedAction) -> SuggestedAction:
        return self.repository.add_suggestion(suggestion)

    def set_status(self, suggestion_id: str, status: str) -> SuggestedAction:
        suggestion = self.repository.get_suggestion(suggestion_id)
        suggestion.status = SuggestionStatus(status)
        suggestion.acted_at = now_iso()
        return self.repository.update_suggestion(suggestion)

