from __future__ import annotations

import pytest

from netops.domain.models import Opportunity, RelationshipLink, Signal, V1Interaction
from netops.domain.validation import UserInputError


def test_v1_relationship_entities_accept_long_form_context():
    interaction = V1Interaction(summary="Met Henry.\nDiscussed cybersecurity.", action_items="Schedule mock interview.")
    signal = Signal(person_id="person-1", signal_text="Values persistence.\nRespects execution.")
    opportunity = Opportunity(title="Mock Interview", description="Practice behavioral and technical questions.")
    link = RelationshipLink(
        source_entity_type="person",
        source_entity_id="person-1",
        target_entity_type="person",
        target_entity_id="person-2",
        relationship_type="mentor",
        description="Henry mentors Isaac.",
    )

    assert interaction.summary.startswith("Met Henry.")
    assert signal.signal_text.endswith("execution.")
    assert opportunity.status == "open"
    assert link.relationship_type == "mentor"


def test_relationship_link_rejects_out_of_scope_entity_types():
    with pytest.raises(UserInputError):
        RelationshipLink(
            source_entity_type="note",
            source_entity_id="n1",
            target_entity_type="person",
            target_entity_id="p1",
            relationship_type="mentions",
        )
