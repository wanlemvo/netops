from __future__ import annotations

from netops.domain.models import Person, Relationship
from netops.domain.validation import AmbiguousMatchError, NotFoundError
from netops.storage.repositories import NetOpsRepository


class PeopleService:
    def __init__(self, repository: NetOpsRepository) -> None:
        self.repository = repository

    def create_person(
        self,
        *,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        organization: str | None = None,
        tags: list[str] | None = None,
        notes: str | None = None,
    ) -> Person:
        return self.repository.add_person(
            Person(
                display_name=name,
                primary_email=email,
                primary_phone=phone,
                organization=organization,
                tags=tags or [],
                relationship_notes=notes,
            )
        )

    def list_people(self, *, tag: str | None = None, search: str | None = None) -> list[Person]:
        return self.repository.list_people(tag=tag, search=search)

    def resolve_person(self, query: str) -> Person:
        try:
            return self.repository.get_person(query)
        except NotFoundError:
            pass
        matches = [person for person in self.repository.list_people() if person.display_name.lower() == query.lower()]
        if not matches:
            matches = [
                person for person in self.repository.list_people() if query.lower() in person.display_name.lower()
            ]
        if not matches:
            raise NotFoundError(f"No person matched '{query}'. Add them first with `netops people add`.")
        if len(matches) > 1:
            details = ", ".join(f"{person.display_name} ({person.id[:8]})" for person in matches)
            raise AmbiguousMatchError(f"More than one person matched '{query}': {details}. Use an id.")
        return matches[0]

    def add_relationship(
        self,
        person_query: str,
        *,
        relationship_type: str,
        related_person_query: str | None = None,
        notes: str | None = None,
        strength: str | None = None,
    ) -> Relationship:
        person = self.resolve_person(person_query)
        related_person_id = self.resolve_person(related_person_query).id if related_person_query else None
        return self.repository.add_relationship(
            Relationship(
                person_id=person.id,
                related_person_id=related_person_id,
                relationship_type=relationship_type,
                strength=strength,
                notes=notes,
            )
        )

    def dashboard(self):
        return self.repository.dashboard_summary()

    def dossier(self, person_query: str):
        person = self.resolve_person(person_query)
        return self.repository.dossier(person.id)

    def directory_rows(self) -> list[dict[str, str]]:
        rows = []
        for person in self.repository.list_people():
            interactions = self.repository.list_interactions(person.id, limit=1)
            loops = self.repository.list_open_loops(person.id)
            rows.append(
                {
                    "id": person.id,
                    "name": person.display_name,
                    "organization": person.organization or "",
                    "tags": ", ".join(person.tags),
                    "last_interaction": interactions[0].occurred_on.isoformat() if interactions else "",
                    "open_loops": str(len([loop for loop in loops if loop.status.value in {"open", "deferred"}])),
                }
            )
        return rows

