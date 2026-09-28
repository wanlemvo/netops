from __future__ import annotations

from datetime import date, timedelta

from netops.domain.models import Interaction, OpenLoop, Person
from netops.domain.suggestions import generate_suggestions
from netops.storage import NetOpsRepository, connect


def test_overdue_open_loop_gets_high_priority(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(Person(display_name="Avery Chen"))
    repository.add_open_loop(
        OpenLoop(person_id=person.id, description="Send migration notes", due_on=date.today() - timedelta(days=1))
    )
    suggestions = generate_suggestions(repository)
    assert suggestions[0].priority_score >= 100
    assert "overdue" in suggestions[0].reason


def test_empty_history_generates_low_priority_first_log_suggestion(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(Person(display_name="Avery Chen"))
    suggestions = generate_suggestions(repository)
    assert suggestions[0].person_id == person.id
    assert suggestions[0].priority_score == 20


def test_stale_contact_generates_check_in_suggestion(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    person = repository.add_person(Person(display_name="Avery Chen"))
    repository.add_interaction(
        Interaction(
            person_id=person.id,
            occurred_on=date.today() - timedelta(days=45),
            interaction_type="email",
            notes="Quarterly check-in",
        )
    )
    suggestions = generate_suggestions(repository)
    assert suggestions[0].action_text == "Check in with Avery Chen"
    assert suggestions[0].priority_score == 35
