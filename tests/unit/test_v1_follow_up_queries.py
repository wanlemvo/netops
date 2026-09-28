from __future__ import annotations

from netops.services import PeopleService


def test_v1_follow_up_query_orders_dated_items_and_filters_closed_opportunities(v1_repository):
    people = PeopleService(v1_repository)
    henry = people.create_v1_person(name="Henry Valentine", next_action="Schedule mock interview.", follow_up_date="2026-06-15")
    people.create_v1_person(name="Dr Olav", next_action="Send follow-up.", follow_up_date="2026-06-12")
    people.add_opportunity([henry.person_id], title="Open Portfolio Review", follow_up_date="2026-06-14")
    people.add_opportunity([henry.person_id], title="Closed Referral", status="closed", follow_up_date="2026-06-11")

    rows = v1_repository.list_v1_follow_ups()

    assert [row["title"] for row in rows] == ["Dr Olav", "Open Portfolio Review", "Henry Valentine"]
    assert "Closed Referral" not in [row["title"] for row in rows]
