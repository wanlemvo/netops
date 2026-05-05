# Implementation Plan: NetOps CLI App

**Branch**: `001-netops-cli-app` | **Date**: 2026-05-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-netops-cli-app/spec.md`

## Summary

Build NetOps as a local-first Python command-line application with two user-facing entry paths: direct commands for fast actions and an interactive terminal interface for guided navigation. The implementation will use a shared domain and storage layer so people, relationships, interactions, open loops, suggestions, and evaluations behave consistently across both modes.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Typer for command routing, Rich for terminal formatting, Textual for the TUI, Pydantic for validation models  
**Storage**: Local SQLite database managed through the Python standard library `sqlite3` module with migration scripts  
**Testing**: pytest for unit, integration, command contract, and TUI smoke tests  
**Target Platform**: Local terminal on Windows, macOS, and Linux  
**Project Type**: Single-package CLI/TUI application  
**Performance Goals**: Suggestions display in under 5 seconds for 1,000 people and 10,000 interactions; common record lookups complete interactively without perceptible delay  
**Constraints**: Offline-capable, single local user, beginner-friendly prompts and errors, no hosted service dependency, command mode and TUI must use the same business logic  
**Scale/Scope**: Personal relationship network with up to 1,000 people, 10,000 interactions, 5,000 open-loop records, and 5,000 evaluations for v1 planning

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The current constitution file is still the default placeholder template and defines no ratified principles, constraints, or governance gates. No enforceable constitution violations are present.

Post-design re-check: PASS. The generated design keeps one application package, shared domain services, local storage, explicit contracts, and testable workflows. No constitution gates were available to violate.

## Project Structure

### Documentation (this feature)

```text
specs/001-netops-cli-app/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- cli-commands.md
|   `-- tui-screens.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
pyproject.toml
src/
`-- netops/
    |-- __init__.py
    |-- __main__.py
    |-- cli.py
    |-- tui/
    |   |-- __init__.py
    |   |-- app.py
    |   `-- screens.py
    |-- domain/
    |   |-- __init__.py
    |   |-- models.py
    |   |-- suggestions.py
    |   `-- validation.py
    |-- storage/
    |   |-- __init__.py
    |   |-- database.py
    |   |-- migrations.py
    |   `-- repositories.py
    `-- services/
        |-- __init__.py
        |-- people.py
        |-- interactions.py
        |-- open_loops.py
        |-- suggestions.py
        `-- evaluations.py

tests/
|-- contract/
|   |-- test_cli_commands.py
|   `-- test_tui_screens.py
|-- integration/
|   |-- test_command_tui_consistency.py
|   |-- test_persistence.py
|   `-- test_suggestions.py
`-- unit/
    |-- test_models.py
    |-- test_repositories.py
    `-- test_suggestion_rules.py
```

**Structure Decision**: Use a single Python package with separate adapters for direct CLI and TUI. Both adapters call shared services, which call domain logic and storage repositories. This keeps beginner-facing interfaces consistent while avoiding duplicate behavior.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
