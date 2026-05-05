from __future__ import annotations

import json
from datetime import date
from typing import Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from netops.domain.validation import AmbiguousMatchError, NetOpsError, format_validation_error
from netops.services import EvaluationService, InteractionService, OpenLoopService, PeopleService, SuggestionService
from netops.storage import NetOpsRepository, connect

app = typer.Typer(help="NetOps tracks people, interactions, follow-ups, suggestions, and outcomes.")
people_app = typer.Typer(help="Manage people.")
relationship_app = typer.Typer(help="Manage relationship context.")
loops_app = typer.Typer(help="Manage open loops and follow-ups.")
app.add_typer(people_app, name="people")
app.add_typer(relationship_app, name="relationship")
app.add_typer(loops_app, name="loops")
console = Console()


def parse_date(value: str | None, *, default_today: bool = False) -> date | None:
    if value in (None, ""):
        return date.today() if default_today else None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Date must use YYYY-MM-DD format: {value}") from exc


def services():
    repository = NetOpsRepository(connect())
    people = PeopleService(repository)
    interactions = InteractionService(repository, people)
    loops = OpenLoopService(repository, people)
    suggestions = SuggestionService(repository, people)
    evaluations = EvaluationService(repository, people)
    return repository, people, interactions, loops, suggestions, evaluations


def fail(error: Exception) -> None:
    message = format_validation_error(error) if isinstance(error, (ValidationError, ValueError)) else str(error)
    console.print(f"[red]Error:[/] {message}")
    raise typer.Exit(1)


def model_json(items) -> str:
    if isinstance(items, list):
        return json.dumps([item.model_dump(mode="json") for item in items], indent=2)
    return json.dumps(items.model_dump(mode="json"), indent=2)


@app.command()
def tui() -> None:
    """Launch the interactive terminal interface."""
    from netops.tui import NetOpsTui

    NetOpsTui().run()


@people_app.command("add")
def people_add(
    name: str = typer.Option(..., "--name", prompt=True, help="Display name."),
    email: Optional[str] = typer.Option(None, "--email", help="Primary email."),
    phone: Optional[str] = typer.Option(None, "--phone", help="Primary phone."),
    organization: Optional[str] = typer.Option(None, "--organization", help="Organization or group."),
    tag: list[str] = typer.Option([], "--tag", help="Repeatable person tag."),
    notes: Optional[str] = typer.Option(None, "--notes", help="Relationship notes."),
) -> None:
    try:
        _, people, *_ = services()
        person = people.create_person(name=name, email=email, phone=phone, organization=organization, tags=tag, notes=notes)
    except Exception as exc:  # pragma: no cover - exercised through CLI tests
        fail(exc)
    console.print(f"[green]Created person[/] {person.display_name} ({person.id})")


@people_app.command("list")
def people_list(
    tag: Optional[str] = typer.Option(None, "--tag"),
    search: Optional[str] = typer.Option(None, "--search"),
    as_json: bool = typer.Option(False, "--json", help="Return JSON."),
) -> None:
    try:
        _, people, *_ = services()
        rows = people.list_people(tag=tag, search=search)
    except Exception as exc:
        fail(exc)
    if as_json:
        console.print(model_json(rows))
        return
    if not rows:
        console.print("No people yet. Add one with `netops people add --name NAME`.")
        return
    table = Table("ID", "Name", "Organization", "Tags")
    for person in rows:
        table.add_row(person.id[:8], person.display_name, person.organization or "", ", ".join(person.tags))
    console.print(table)


@relationship_app.command("add")
def relationship_add(
    person: str = typer.Argument(...),
    relationship_type: str = typer.Option(..., "--type", prompt=True),
    related_person: Optional[str] = typer.Option(None, "--related-person"),
    notes: Optional[str] = typer.Option(None, "--notes"),
) -> None:
    try:
        _, people, *_ = services()
        relationship = people.add_relationship(
            person,
            relationship_type=relationship_type,
            related_person_query=related_person,
            notes=notes,
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved relationship[/] {relationship.relationship_type} ({relationship.id})")


@app.command("log")
def log_interaction(
    person: str = typer.Argument(...),
    occurred_on: Optional[str] = typer.Option(None, "--date"),
    interaction_type: str = typer.Option(..., "--type", prompt=True),
    notes: str = typer.Option(..., "--notes", prompt=True),
    follow_up: Optional[str] = typer.Option(None, "--follow-up"),
    due: Optional[str] = typer.Option(None, "--due"),
    allow_future: bool = typer.Option(False, "--allow-future"),
) -> None:
    try:
        _, _, interactions, *_ = services()
        interaction, loop = interactions.log_interaction(
            person,
            occurred_on=parse_date(occurred_on, default_today=True),
            interaction_type=interaction_type,
            notes=notes,
            follow_up=follow_up,
            due_on=parse_date(due),
            allow_future=allow_future,
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved interaction[/] {interaction.id}")
    if loop:
        console.print(f"[green]Created open loop[/] {loop.description} ({loop.id})")


@loops_app.command("list")
def loops_list(
    person: Optional[str] = typer.Option(None, "--person"),
    status: Optional[str] = typer.Option(None, "--status"),
    overdue: bool = typer.Option(False, "--overdue"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    try:
        _, _, _, loops, *_ = services()
        rows = loops.list(person_query=person, status=status, overdue=overdue)
    except Exception as exc:
        fail(exc)
    if as_json:
        console.print(model_json(rows))
        return
    if not rows:
        console.print("No open loops match that view.")
        return
    table = Table("ID", "Person", "Status", "Due", "Description")
    repository = services()[0]
    for loop in rows:
        table.add_row(loop.id[:8], repository.get_person(loop.person_id).display_name, loop.status.value, str(loop.due_on or ""), loop.description)
    console.print(table)


@loops_app.command("close")
def loops_close(
    loop_id: str = typer.Argument(...),
    status: str = typer.Option(..., "--status"),
    notes: Optional[str] = typer.Option(None, "--notes"),
    due: Optional[str] = typer.Option(None, "--due"),
) -> None:
    try:
        _, _, _, loops, *_ = services()
        loop = loops.close(loop_id, status=status, notes=notes, due_on=parse_date(due))
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Updated open loop[/] {loop.id} -> {loop.status.value}")


@app.command("suggest")
def suggest(
    person: Optional[str] = typer.Option(None, "--person"),
    limit: int = typer.Option(10, "--limit"),
    include_low_priority: bool = typer.Option(False, "--include-low-priority"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    try:
        _, people, _, _, suggestions, _ = services()
        rows = suggestions.generate(person_query=person, limit=limit, include_low_priority=include_low_priority)
    except Exception as exc:
        fail(exc)
    if as_json:
        console.print(model_json(rows))
        return
    if not rows:
        console.print("No useful suggestions right now.")
        return
    table = Table("Priority", "Person", "Action", "Reason")
    for item in rows:
        try:
            person_name = people.repository.get_person(item.person_id).display_name
        except NetOpsError:
            person_name = item.person_id[:8]
        table.add_row(str(item.priority_score), person_name, item.action_text, item.reason)
    console.print(table)


@app.command("evaluate")
def evaluate(
    person: Optional[str] = typer.Option(None, "--person"),
    action: Optional[str] = typer.Option(None, "--action"),
    interaction: Optional[str] = typer.Option(None, "--interaction"),
    outcome: str = typer.Option(..., "--outcome", prompt=True),
    notes: Optional[str] = typer.Option(None, "--notes"),
    evaluated_on: Optional[str] = typer.Option(None, "--date"),
) -> None:
    try:
        *_, evaluations = services()
        evaluation = evaluations.create(
            person_query=person,
            suggested_action_id=action,
            interaction_id=interaction,
            outcome=outcome,
            notes=notes,
            evaluated_on=parse_date(evaluated_on, default_today=True),
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved evaluation[/] {evaluation.outcome.value} ({evaluation.id})")
