from __future__ import annotations

from netops.domain.models import V1Person
from netops.services.people import PeopleService


def test_people_service_scaffold_accepts_v1_repository(v1_repository):
    service = PeopleService(v1_repository)
    person = v1_repository.add_v1_person(V1Person(name="Henry Valentine", relationship_strength="high"))

    resolved = service.resolve_person(person.person_id)

    assert resolved.display_name == "Henry Valentine"


def test_people_service_creates_and_reopens_complete_v1_record(v1_repository):
    service = PeopleService(v1_repository)

    created = service.create_v1_person(
        name="Henry Valentine",
        alias="Henry",
        role="Senior Manager, Cybersecurity",
        organization="T-Mobile",
        location="Bellevue, WA",
        birthday="2026-06",
        relationship_type="mentor",
        relationship_status="active",
        relationship_strength="Medium-High",
        origin_story="Introduced through T-Mobile network.",
        importance_reason="Strong cybersecurity connection.",
        dossier="Cybersecurity leader.\nOffered mock interview support.",
        interests="Cybersecurity\nLeadership",
        communication_style="Direct and practical.",
        preferences="Values initiative.",
        current_goals="Developing cybersecurity talent.",
        potential_value="Mentorship and career guidance.",
        first_met="2026-06",
        last_contact="2026-06",
        next_action="Schedule mock interview.",
        follow_up_date="2026-06-15",
        tags=["cybersecurity", "mentor"],
    )

    reopened = service.get_v1_person(created.person_id)

    assert reopened.name == "Henry Valentine"
    assert reopened.relationship_strength == "Medium-High"
    assert reopened.dossier == "Cybersecurity leader.\nOffered mock interview support."
    assert reopened.next_action == "Schedule mock interview."
    assert service.resolve_person("Henry Valentine").tags == ["cybersecurity", "mentor"]


def test_people_service_updates_v1_field_and_keeps_name_resolvable(v1_repository):
    service = PeopleService(v1_repository)
    created = service.create_v1_person(name="Dr Olav", relationship_strength="trusted advisor")

    updated = service.update_v1_person_field(created.person_id, "name", "Dr Olav Opedal")

    assert updated.name == "Dr Olav Opedal"
    assert service.resolve_person("Dr Olav Opedal").display_name == "Dr Olav Opedal"


def test_people_service_editable_fields_include_v1_context(v1_repository):
    service = PeopleService(v1_repository)
    created = service.create_v1_person(name="Avery Chen", origin_story="Met through platform work.")

    fields = {field.key: field for field in service.editable_fields(created.person_id)}

    assert "origin_story" in fields
    assert "mutual_connections" not in fields
    assert fields["origin_story"].current_value == "Met through platform work."
