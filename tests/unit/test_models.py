from __future__ import annotations

import pytest
from pydantic import ValidationError

from netops.domain.models import Evaluation, EvaluationOutcome, Person, Relationship


def test_person_requires_display_name():
    with pytest.raises(ValidationError):
        Person(display_name="")


def test_tags_normalize_from_string():
    person = Person(display_name="Avery", tags="mentor, northwind")
    assert person.tags == ["mentor", "northwind"]


def test_relationship_cannot_link_person_to_self():
    with pytest.raises(ValidationError):
        Relationship(person_id="p1", related_person_id="p1", relationship_type="mentor")


def test_evaluation_can_record_person_level_outcome():
    evaluation = Evaluation(person_id="p1", outcome=EvaluationOutcome.POSITIVE)
    assert evaluation.outcome == EvaluationOutcome.POSITIVE
