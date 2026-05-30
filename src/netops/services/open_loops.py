from __future__ import annotations

from datetime import date

from netops.domain.models import OpenLoop, OpenLoopStatus
from netops.storage.repositories import NetOpsRepository


class OpenLoopService:
    def __init__(self, repository: NetOpsRepository, people_service) -> None:
        self.repository = repository
        self.people_service = people_service

    def create(
        self,
        person_query: str,
        description: str,
        *,
        due_on: date | None = None,
        priority: int | None = None,
    ) -> OpenLoop:
        person = self.people_service.resolve_person(person_query)
        return self.repository.add_open_loop(
            OpenLoop(person_id=person.id, description=description, due_on=due_on, priority=priority)
        )

    def list(self, *, person_query: str | None = None, status: str | None = None, overdue: bool = False) -> list[OpenLoop]:
        person_id = self.people_service.resolve_person(person_query).id if person_query else None
        loop_status = OpenLoopStatus(status) if status else None
        return self.repository.list_open_loops(person_id, status=loop_status, overdue=overdue)

    def close(
        self,
        loop_id: str,
        *,
        status: str,
        notes: str | None = None,
        due_on: date | None = None,
    ) -> OpenLoop:
        loop = self.repository.get_open_loop(loop_id)
        loop.status = OpenLoopStatus(status)
        loop.resolution_notes = notes
        loop.due_on = due_on
        return self.repository.update_open_loop(loop)

    def delete(self, loop_id: str) -> None:
        self.repository.delete_open_loop(loop_id)
