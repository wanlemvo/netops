from __future__ import annotations

from netops.services import InteractionService, PeopleService


def test_multi_person_v1_interaction_is_visible_for_each_person(v1_repository):
    people = PeopleService(v1_repository)
    interactions = InteractionService(v1_repository, people)
    henry = people.create_v1_person(name="Harper Vale")
    benjamin = people.create_v1_person(name="Blair Reed")

    created = interactions.log_v1_interaction(
        [henry.person_id, benjamin.person_id],
        interaction_date="2026-06-10",
        interaction_type="meeting",
        summary="Discussed cybersecurity careers.",
        takeaways="Persistence matters.",
        action_items="Schedule mock interview.",
    )

    assert v1_repository.list_v1_interactions_for_person(henry.person_id)[0].interaction_id == created.interaction_id
    assert v1_repository.list_v1_interactions_for_person(benjamin.person_id)[0].interaction_id == created.interaction_id
