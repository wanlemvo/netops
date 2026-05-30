from __future__ import annotations

from netops.services import PeopleService
from netops.storage import NetOpsRepository, connect


def test_minimal_person_opens_as_dossier_after_migration(isolated_db):
    repository = NetOpsRepository(connect(isolated_db))
    service = PeopleService(repository)
    person = service.create_person(name="Avery Chen")
    dossier = service.dossier(person.id)
    assert dossier.person.display_name == "Avery Chen"
    assert dossier.person.interests == []
    assert dossier.raw_notes == []
