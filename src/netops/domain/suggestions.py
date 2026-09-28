from __future__ import annotations

from datetime import date, timedelta

from netops.domain.models import OpenLoopStatus, SuggestedAction


def generate_suggestions(repository, *, person_id: str | None = None) -> list[SuggestedAction]:
    suggestions: list[SuggestedAction] = []
    people = [repository.get_person(person_id)] if person_id else repository.list_people()
    today = date.today()

    for person in people:
        loops = repository.list_open_loops(person.id)
        open_loops = [loop for loop in loops if loop.status in {OpenLoopStatus.OPEN, OpenLoopStatus.DEFERRED}]
        evaluations = repository.list_evaluations(person.id)
        recent_negative = any(evaluation.outcome.value == "negative" for evaluation in evaluations[:3])

        for loop in open_loops:
            score = 60
            reasons = ["open loop"]
            if loop.due_on and loop.due_on < today:
                score += 40
                reasons.append(f"overdue since {loop.due_on.isoformat()}")
            elif loop.due_on and loop.due_on <= today + timedelta(days=7):
                score += 25
                reasons.append(f"due soon on {loop.due_on.isoformat()}")
            if recent_negative:
                score -= 10
                reasons.append("recent negative outcome suggests a careful tone")
            suggestions.append(
                SuggestedAction(
                    id=f"loop-{loop.id}",
                    person_id=person.id,
                    open_loop_id=loop.id,
                    action_text=f"Follow up with {person.display_name}: {loop.description}",
                    reason=", ".join(reasons),
                    priority_score=max(score, 1),
                )
            )

        last_interactions = repository.list_interactions(person.id, limit=1)
        if not open_loops and last_interactions:
            days = (today - last_interactions[0].occurred_on).days
            if days >= 30:
                suggestions.append(
                    SuggestedAction(
                        id=f"checkin-{person.id}",
                        person_id=person.id,
                        action_text=f"Check in with {person.display_name}",
                        reason=f"last interaction was {days} days ago",
                        priority_score=35 if days < 90 else 50,
                    )
                )
        elif not open_loops and not last_interactions:
            suggestions.append(
                SuggestedAction(
                    id=f"firstlog-{person.id}",
                    person_id=person.id,
                    action_text=f"Log first interaction with {person.display_name}",
                    reason="no interaction history exists yet",
                    priority_score=20,
                )
            )

    suggestions.sort(key=lambda suggestion: (-suggestion.priority_score, suggestion.action_text.lower()))
    return suggestions
