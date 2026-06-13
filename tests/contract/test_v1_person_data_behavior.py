from __future__ import annotations

from netops.domain.models import V1Person


def test_v1_person_accepts_required_name_with_optional_fields_unset():
    person = V1Person(name="Isaac")

    assert person.name == "Isaac"
    assert person.alias is None
    assert person.origin_story is None
    assert person.follow_up_date is None


def test_v1_person_preserves_multiline_profile_intelligence():
    person = V1Person(
        name="Henry Valentine",
        dossier="Cybersecurity leader.\nStrong advocate for persistence.",
        importance_reason="Provides strategic career guidance.\nInvested personal time.",
    )

    assert "\n" in person.dossier
    assert person.importance_reason.endswith("Invested personal time.")


def test_v1_person_relationship_strength_is_text_not_numeric_score():
    person = V1Person(name="Rei", relationship_strength="Medium-High / trusted")

    assert person.relationship_strength == "Medium-High / trusted"
