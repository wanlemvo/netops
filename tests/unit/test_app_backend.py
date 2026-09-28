from __future__ import annotations

import json

from netops.services.app_backend import NetworkOpsBackend


def test_backend_returns_mockup_shaped_dossier(v1_repository):
    backend = NetworkOpsBackend(v1_repository)
    henry = backend.create_person(
        {
            "name": "Henry Valentine",
            "alias": "Henry",
            "role": "Senior Manager, Cybersecurity",
            "organization": "T-Mobile",
            "location": "Bellevue, WA",
            "relationship_type": "mentor",
            "relationship_status": "active",
            "relationship_strength": "Medium-High",
            "importance_reason": "One of my strongest cybersecurity connections.",
            "dossier": "Cybersecurity leader.\nStrong advocate for persistence.",
            "interests": "Cybersecurity\nLeadership\nMentorship",
            "communication_style": "Direct\nPractical\nAction-oriented",
            "potential_value": "Mentorship\nMock interviews\nCybersecurity insight",
            "next_action": "Schedule mock interview.",
            "follow_up_date": "2026-06-15",
            "email": "henry@example.com",
            "phone": "555-0100",
            "tags": ["cybersecurity", "mentor", "tmobile"],
        }
    )
    isaac = backend.create_person({"name": "Isaac", "relationship_type": "self"})

    interaction = backend.add_interaction(
        {
            "people": [henry["person_id"], isaac["person_id"]],
            "interaction_date": "2026-06-03",
            "interaction_type": "meeting",
            "summary": "Discussed cybersecurity careers and persistence.",
            "takeaways": "Be persistent.\nFocus on execution.",
            "action_items": "Prepare resume.\nSchedule mock interview.",
            "follow_up_required": True,
            "follow_up_date": "2026-06-15",
        }
    )
    backend.add_signal(
        henry["person_id"],
        {
            "text": "Values persistence.",
            "confidence": "high",
            "source_interaction_id": interaction["interaction_id"],
        },
    )
    backend.add_opportunity(
        {
            "people": [henry["person_id"], isaac["person_id"]],
            "title": "Mock Interview",
            "status": "open",
            "description": "Practice cybersecurity interview loops.",
            "follow_up_date": "2026-06-15",
        }
    )
    backend.add_relationship_link(
        {
            "source_person_id": henry["person_id"],
            "target_person_id": isaac["person_id"],
            "relationship_type": "mentor",
            "description": "Henry mentors Isaac.",
        }
    )

    dossier = backend.get_dossier(henry["person_id"])

    assert dossier["view"] == "dossier"
    assert dossier["header"]["title"] == "Henry Valentine"
    assert "Cybersecurity leader." in dossier["current_read"]
    assert dossier["identity_records"]["tags"] == ["cybersecurity", "mentor", "tmobile"]
    assert len(dossier["contact_records"]["methods"]) == 2
    assert dossier["dossier_folders"] == [
        {"id": "identity", "label": "Full Identity File", "count": 1},
        {"id": "contacts", "label": "All Contact Methods", "count": 2},
        {"id": "interactions", "label": "Interaction Archive", "count": 1},
        {"id": "signals", "label": "Signal Ledger", "count": 1},
        {"id": "opportunities", "label": "Opportunity Map", "count": 1},
        {"id": "connections", "label": "Relationship Links", "count": 1},
    ]
    assert dossier["folder_payloads"]["interactions"][0]["takeaways"] == "Be persistent.\nFocus on execution."
    assert dossier["folder_payloads"]["signals"][0]["text"] == "Values persistence."
    assert dossier["folder_payloads"]["opportunities"][0]["title"] == "Mock Interview"
    assert dossier["connections"][0]["other_entity_label"] == "Isaac"
    json.dumps(dossier)


def test_backend_overview_is_json_safe_and_filters_people(v1_repository):
    backend = NetworkOpsBackend(v1_repository)
    backend.create_person({"name": "Marcus Rivera", "tags": ["recruiting", "ai"], "next_action": "Send resume"})
    backend.create_person({"name": "Rei", "tags": ["engineering"]})
    backend.add_signal("Marcus Rivera", {"text": "Hiring window mentioned.", "confidence": "medium"})

    overview = backend.get_overview()
    filtered = backend.list_people(search="marc", tag="recruiting")

    assert overview["system_state"]["files"] == 2
    assert overview["system_state"]["open_loops"] == 1
    assert overview["recent_intel"][0]["text"] == "Hiring window mentioned."
    assert filtered[0]["name"] == "Marcus Rivera"
    json.dumps(overview)


def test_backend_tolerates_invalid_legacy_date_values(v1_repository):
    backend = NetworkOpsBackend(v1_repository)
    created = backend.create_person({"name": "Dr Olav Opedal"})
    v1_repository.connection.execute(
        "UPDATE people SET birthday = ?, follow_up_date = ? WHERE person_id = ?",
        ("k", "soon-ish", created["person_id"]),
    )
    v1_repository.connection.commit()

    overview = backend.get_overview()
    person = backend.get_person(created["person_id"])

    assert overview["people"][0]["name"] == "Dr Olav Opedal"
    assert person["birthday"] is None
    assert person["follow_up_date"] is None
    json.dumps(overview)


def test_backend_updates_person_tags_and_long_text(v1_repository):
    backend = NetworkOpsBackend(v1_repository)
    person = backend.create_person({"name": "Dr. Olav", "tags": ["tmobile"]})

    updated = backend.update_person(
        person["person_id"],
        {
            "name": "Dr Olav Opedal",
            "dossier": "Line one.\nLine two.\nLine three.",
            "tags": ["tmobile", "ai"],
        },
    )

    assert updated["name"] == "Dr Olav Opedal"
    assert updated["dossier"] == "Line one.\nLine two.\nLine three."
    assert updated["tags"] == ["tmobile", "ai"]
