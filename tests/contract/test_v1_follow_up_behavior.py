from __future__ import annotations

from netops.domain.models import Opportunity, V1Person


def test_v1_follow_up_fields_are_plain_visibility_fields():
    person = V1Person(name="Henry Valentine", next_action="Schedule mock interview.", follow_up_date="2026-06-15")
    opportunity = Opportunity(title="Mock Interview", status="open", follow_up_date="2026-06-15")

    assert person.next_action == "Schedule mock interview."
    assert person.follow_up_date == "2026-06-15"
    assert opportunity.status == "open"
    assert opportunity.follow_up_date == "2026-06-15"
