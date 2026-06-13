from __future__ import annotations

from netops.domain.models import (
    InteractionPerson,
    Opportunity,
    OpportunityPerson,
    RelationshipLink,
    Signal,
    V1Interaction,
    V1Person,
)


def test_v1_long_form_text_round_trips_across_relationship_entities(v1_repository):
    long_text = ("Line one with context.\n" + "A" * 2000 + "\nFinal line.") * 2
    person = v1_repository.add_v1_person(V1Person(name="Henry Valentine", dossier=long_text, origin_story=long_text))

    draft_interaction = V1Interaction(summary=long_text, takeaways=long_text, action_items=long_text)
    interaction = v1_repository.add_v1_interaction(
        draft_interaction,
        [InteractionPerson(interaction_id=draft_interaction.interaction_id, person_id=person.person_id, is_primary=1)],
    )
    signal = v1_repository.add_signal(Signal(person_id=person.person_id, signal_text=long_text))
    draft_opportunity = Opportunity(title="Mock Interview", description=long_text)
    opportunity = v1_repository.add_opportunity(
        draft_opportunity,
        [OpportunityPerson(opportunity_id=draft_opportunity.opportunity_id, person_id=person.person_id, is_primary=1)],
    )
    link = v1_repository.add_relationship_link(
        RelationshipLink(
            source_entity_type="person",
            source_entity_id=person.person_id,
            target_entity_type="signal",
            target_entity_id=signal.signal_id,
            relationship_type="generated",
            description=long_text,
        )
    )

    assert v1_repository.get_v1_person(person.person_id).dossier == long_text
    assert v1_repository.list_v1_interactions_for_person(person.person_id)[0].summary == long_text
    assert v1_repository.list_signals(person.person_id)[0].signal_text == long_text
    assert v1_repository.list_opportunities_for_person(person.person_id)[0].description == long_text
    assert v1_repository.list_relationship_links_for_entity("person", person.person_id)[0].description == link.description == long_text
