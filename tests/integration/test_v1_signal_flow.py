from __future__ import annotations

from netops.services import InteractionService, PeopleService


def test_signal_can_reference_source_interaction(v1_repository):
    people = PeopleService(v1_repository)
    interactions = InteractionService(v1_repository, people)
    henry = people.create_v1_person(name="Harper Vale")
    interaction = interactions.log_v1_interaction(
        [henry.person_id],
        interaction_date="2026-06-10",
        interaction_type="meeting",
        summary="Discussed persistence.",
    )

    signal = people.add_signal(
        henry.person_id,
        text="Values persistence.",
        confidence="high",
        source_interaction_id=interaction.interaction_id,
    )

    saved = people.list_signals(henry.person_id)[0]
    assert saved.signal_id == signal.signal_id
    assert saved.source_interaction_id == interaction.interaction_id
