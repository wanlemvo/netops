from __future__ import annotations

from pathlib import Path


def test_v1_quickstart_covers_implemented_scenarios():
    quickstart = Path("specs/004-person-intelligence-record/quickstart.md").read_text()

    for expected in [
        "Create Minimal Person",
        "Add Full Person Intelligence Record",
        "Add Contact Methods",
        "Add Multi-Person Interaction",
        "Add Signal From Interaction",
        "Add Multi-Person Opportunity",
        "Add Person-To-Person Relationship Link",
        "Profile Photo",
        "Long Multiline Text",
        "Legacy Data Compatibility",
    ]:
        assert expected in quickstart
