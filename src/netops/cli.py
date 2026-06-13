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
contact_app = typer.Typer(help="Manage person contact methods.")
relationship_app = typer.Typer(help="Manage relationship context.")
signal_app = typer.Typer(help="Manage relationship signals.")
opportunity_app = typer.Typer(help="Manage relationship opportunities.")
loops_app = typer.Typer(help="Manage open loops and follow-ups.")
app.add_typer(people_app, name="people")
people_app.add_typer(contact_app, name="contact")
app.add_typer(relationship_app, name="relationship")
app.add_typer(signal_app, name="signal")
app.add_typer(opportunity_app, name="opportunity")
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
    linkedin: Optional[str] = typer.Option(None, "--linkedin", help="LinkedIn profile."),
    github: Optional[str] = typer.Option(None, "--github", help="GitHub profile."),
    other_social: Optional[str] = typer.Option(None, "--other-social", help="Other social/contact URL."),
    alias: Optional[str] = typer.Option(None, "--alias", help="Alias or familiar name."),
    role: Optional[str] = typer.Option(None, "--role", help="Role or title."),
    organization: Optional[str] = typer.Option(None, "--organization", help="Organization or group."),
    location: Optional[str] = typer.Option(None, "--location", help="Location."),
    birthday: Optional[str] = typer.Option(None, "--birthday", help="Birthday as YYYY-MM-DD or YYYY-MM."),
    profile_photo_path: Optional[str] = typer.Option(None, "--profile-photo", help="Local profile photo path."),
    relationship_type: Optional[str] = typer.Option(None, "--relationship-type", help="Relationship type."),
    relationship_status: Optional[str] = typer.Option(None, "--relationship-status", help="Relationship status."),
    relationship_strength: Optional[str] = typer.Option(None, "--relationship-strength", help="Relationship strength text."),
    origin_story: Optional[str] = typer.Option(None, "--origin-story", help="How this relationship began."),
    importance_reason: Optional[str] = typer.Option(None, "--importance-reason", help="Why this person matters."),
    dossier: Optional[str] = typer.Option(None, "--dossier", help="Long-form person dossier."),
    interests: Optional[str] = typer.Option(None, "--interests", help="Long-form interests/intelligence."),
    communication_style: Optional[str] = typer.Option(None, "--communication-style", help="Communication style."),
    preferences: Optional[str] = typer.Option(None, "--preferences", help="Known preferences."),
    current_goals: Optional[str] = typer.Option(None, "--current-goals", help="Current goals."),
    potential_value: Optional[str] = typer.Option(None, "--potential-value", help="Potential relationship value."),
    first_met: Optional[str] = typer.Option(None, "--first-met", help="First met date as YYYY-MM-DD or YYYY-MM."),
    last_contact: Optional[str] = typer.Option(None, "--last-contact", help="Last contact date as YYYY-MM-DD or YYYY-MM."),
    next_action: Optional[str] = typer.Option(None, "--next-action", help="Next relationship action."),
    follow_up_date: Optional[str] = typer.Option(None, "--follow-up-date", help="Follow-up date as YYYY-MM-DD or YYYY-MM."),
    tag: list[str] = typer.Option([], "--tag", help="Repeatable person tag."),
    notes: Optional[str] = typer.Option(None, "--notes", help="Relationship notes."),
) -> None:
    try:
        _, people, *_ = services()
        person = people.create_v1_person(
            name=name,
            alias=alias,
            role=role,
            organization=organization,
            location=location,
            birthday=birthday,
            profile_photo_path=profile_photo_path,
            relationship_type=relationship_type,
            relationship_status=relationship_status,
            relationship_strength=relationship_strength,
            origin_story=origin_story,
            importance_reason=importance_reason,
            dossier=dossier or notes,
            interests=interests,
            communication_style=communication_style,
            preferences=preferences,
            current_goals=current_goals,
            potential_value=potential_value,
            first_met=first_met,
            last_contact=last_contact,
            next_action=next_action,
            follow_up_date=follow_up_date,
            tags=tag,
        )
        for kind, label, value in [
            ("email", "primary", email),
            ("phone", "primary", phone),
            ("social", "LinkedIn", linkedin),
            ("social", "GitHub", github),
            ("social", "Other", other_social),
        ]:
            if value:
                people.add_contact(person.person_id, kind=kind, label=label, value=value)
    except Exception as exc:  # pragma: no cover - exercised through CLI tests
        fail(exc)
    console.print(f"[green]Created person[/] {person.name} ({person.person_id})")


@people_app.command("show")
def people_show(
    person: str = typer.Argument(...),
    as_json: bool = typer.Option(False, "--json", help="Return JSON."),
) -> None:
    try:
        _, people, *_ = services()
        record = people.get_v1_person(person)
    except Exception as exc:
        fail(exc)
    if as_json:
        typer.echo(model_json(record))
        return
    table = Table("Field", "Value")
    for field, value in record.model_dump(mode="json").items():
        if field.endswith("_at") and field not in {"created_at", "updated_at", "archived_at"}:
            continue
        table.add_row(field, str(value or "unset"))
    console.print(table)


@people_app.command("edit")
def people_edit(
    person: str = typer.Argument(...),
    field: str = typer.Option(..., "--field", help="V1 person field to update."),
    value: str = typer.Option("", "--value", help="New value. Empty clears optional fields."),
) -> None:
    try:
        _, people, *_ = services()
        record = people.update_v1_person_field(person, field, value)
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Updated person[/] {record.name} ({record.person_id})")


@people_app.command("photo")
def people_photo(
    person: str = typer.Argument(...),
    path: str = typer.Option(..., "--path", help="Local profile photo path."),
    no_copy: bool = typer.Option(False, "--no-copy", help="Store only the provided path."),
) -> None:
    try:
        _, people, *_ = services()
        record = people.set_profile_photo(person, path, copy_to_assets=not no_copy)
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Updated profile photo[/] {record.profile_photo_path or 'unset'}")


@contact_app.command("add")
def contact_add(
    person: str = typer.Argument(...),
    kind: str = typer.Option(..., "--type", help="email, phone, linkedin, github, or other."),
    value: str = typer.Option(..., "--value", help="Contact value."),
    label: Optional[str] = typer.Option(None, "--label", help="Optional label."),
    primary: bool = typer.Option(False, "--primary", help="Make primary for this contact type."),
) -> None:
    try:
        _, people, *_ = services()
        contact = people.add_contact_method(person, kind=kind, value=value, label=label, is_primary=primary)
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Added contact[/] {contact.type}:{contact.value} ({contact.contact_method_id})")


@contact_app.command("list")
def contact_list(
    person: str = typer.Argument(...),
    as_json: bool = typer.Option(False, "--json", help="Return JSON."),
) -> None:
    try:
        _, people, *_ = services()
        rows = people.list_contact_methods(person)
    except Exception as exc:
        fail(exc)
    if as_json:
        typer.echo(model_json(rows))
        return
    if not rows:
        console.print("No contact methods for this person.")
        return
    table = Table("ID", "Type", "Label", "Value", "Primary")
    for contact in rows:
        table.add_row(
            contact.contact_method_id[:8],
            contact.type,
            contact.label or "",
            contact.value,
            "yes" if contact.is_primary else "",
        )
    console.print(table)


@contact_app.command("delete")
def contact_delete(contact_id: str = typer.Argument(...)) -> None:
    try:
        _, people, *_ = services()
        people.delete_contact_method(contact_id)
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Deleted contact[/] {contact_id}")


@contact_app.command("set-primary")
def contact_set_primary(contact_id: str = typer.Argument(...)) -> None:
    try:
        _, people, *_ = services()
        contact = people.set_primary_contact_method(contact_id)
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Primary contact[/] {contact.type}:{contact.value}")


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
        typer.echo(model_json(rows))
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


@relationship_app.command("link")
def relationship_link(
    source_person: str = typer.Argument(...),
    target_person: str = typer.Argument(...),
    relationship_type: str = typer.Option(..., "--type", help="Extensible relationship type."),
    description: Optional[str] = typer.Option(None, "--description", help="Optional relationship context."),
) -> None:
    try:
        _, people, *_ = services()
        link = people.add_relationship_link(
            source_person,
            target_person,
            relationship_type=relationship_type,
            description=description,
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved relationship link[/] {link.relationship_type} ({link.relationship_link_id})")


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


@app.command("log-v1")
def log_v1_interaction(
    person: list[str] = typer.Option(..., "--person", help="Repeat for every participant."),
    interaction_date: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD."),
    interaction_type: Optional[str] = typer.Option(None, "--type", help="Interaction type."),
    summary: Optional[str] = typer.Option(None, "--summary", help="Interaction summary."),
    takeaways: Optional[str] = typer.Option(None, "--takeaways", help="Long-form takeaways."),
    action_items: Optional[str] = typer.Option(None, "--action-items", help="Long-form action items."),
    sentiment: Optional[str] = typer.Option(None, "--sentiment", help="Optional sentiment."),
    follow_up_required: bool = typer.Option(False, "--follow-up-required", help="Mark follow-up required."),
    follow_up_date: Optional[str] = typer.Option(None, "--follow-up-date", help="YYYY-MM-DD."),
) -> None:
    try:
        _, _, interactions, *_ = services()
        interaction = interactions.log_v1_interaction(
            person,
            interaction_date=interaction_date or date.today().isoformat(),
            interaction_type=interaction_type,
            summary=summary,
            takeaways=takeaways,
            action_items=action_items,
            sentiment=sentiment,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved interaction[/] {interaction.interaction_id}")


@signal_app.command("add")
def signal_add(
    person: str = typer.Argument(...),
    text: str = typer.Option(..., "--text", help="Signal text."),
    confidence: Optional[str] = typer.Option(None, "--confidence", help="Optional confidence."),
    source_interaction: Optional[str] = typer.Option(None, "--source-interaction", help="Optional source interaction ID."),
    source: Optional[str] = typer.Option(None, "--source", help="Optional source description."),
) -> None:
    try:
        _, people, *_ = services()
        signal = people.add_signal(
            person,
            text=text,
            confidence=confidence,
            source_interaction_id=source_interaction,
            source_description=source,
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved signal[/] {signal.signal_id}")


@signal_app.command("list")
def signal_list(person: str = typer.Argument(...), as_json: bool = typer.Option(False, "--json")) -> None:
    try:
        _, people, *_ = services()
        rows = people.list_signals(person)
    except Exception as exc:
        fail(exc)
    if as_json:
        typer.echo(model_json(rows))
        return
    table = Table("ID", "Signal", "Confidence")
    for signal in rows:
        table.add_row(signal.signal_id[:8], signal.signal_text, signal.confidence or "")
    console.print(table)


@opportunity_app.command("add")
def opportunity_add(
    person: list[str] = typer.Option(..., "--person", help="Repeat for every linked person."),
    title: str = typer.Option(..., "--title", help="Opportunity title."),
    status: str = typer.Option("open", "--status", help="Opportunity status."),
    description: Optional[str] = typer.Option(None, "--description", help="Long-form description."),
    follow_up_date: Optional[str] = typer.Option(None, "--follow-up-date", help="YYYY-MM-DD."),
) -> None:
    try:
        _, people, *_ = services()
        opportunity = people.add_opportunity(
            person,
            title=title,
            status=status,
            description=description,
            follow_up_date=follow_up_date,
        )
    except Exception as exc:
        fail(exc)
    console.print(f"[green]Saved opportunity[/] {opportunity.title} ({opportunity.opportunity_id})")


@opportunity_app.command("list")
def opportunity_list(person: str = typer.Argument(...), as_json: bool = typer.Option(False, "--json")) -> None:
    try:
        _, people, *_ = services()
        rows = people.list_opportunities(person)
    except Exception as exc:
        fail(exc)
    if as_json:
        typer.echo(model_json(rows))
        return
    table = Table("ID", "Title", "Status", "Follow-Up")
    for opportunity in rows:
        table.add_row(opportunity.opportunity_id[:8], opportunity.title, opportunity.status, opportunity.follow_up_date or "")
    console.print(table)


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
        typer.echo(model_json(rows))
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


@loops_app.command("review-v1")
def loops_review_v1(as_json: bool = typer.Option(False, "--json", help="Return JSON.")) -> None:
    try:
        _, _, _, loops, *_ = services()
        rows = loops.review_v1_follow_ups()
    except Exception as exc:
        fail(exc)
    if as_json:
        typer.echo(json.dumps(rows, indent=2))
        return
    if not rows:
        console.print("No V1 follow-ups are pending.")
        return
    table = Table("Kind", "Title", "Person", "Follow-Up", "Status", "Action")
    for row in rows:
        table.add_row(row["kind"], row["title"], row["person"], row["follow_up_date"], row["status"], row["action"])
    console.print(table)


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
        typer.echo(model_json(rows))
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
