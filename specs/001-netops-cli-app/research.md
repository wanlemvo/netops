> Historical design record; not current product instructions. See the [current README](../../README.md).

# Research: NetOps CLI App

## Decision: Python 3.11+ runtime

**Rationale**: The feature explicitly asks for Python, and Python 3.11+ gives modern typing, `tomllib`, better performance than older supported versions, and broad dependency compatibility. It is conservative enough for local use on current Windows, macOS, and Linux machines.

**Alternatives considered**: Python 3.12+ only was considered but rejected for wider compatibility. Python 3.10 was considered but provides less runway for modern typing and package support.

## Decision: Typer for direct command mode

**Rationale**: Typer is designed for Python command-line applications, uses type hints, supports subcommands, automatic help, shell completion, and beginner-friendly error output. This maps cleanly to `log`, `suggest`, and `evaluate` while leaving room for `people`, `loops`, and `tui` command groups. Official docs: https://typer.tiangolo.com/

**Alternatives considered**: `argparse` avoids an extra dependency but requires more manual command organization and validation. Click is mature but Typer provides a more type-driven developer experience and a smaller learning step for this project.

## Decision: Textual for the interactive TUI

**Rationale**: Textual is a Python TUI framework for sophisticated terminal interfaces, with screens, widgets, layouts, keyboard handling, and an explicit testing story. Its screen model fits dashboard, directory, dossier, timeline, suggestions, and evaluation views. Official docs: https://textual.textualize.io/

**Alternatives considered**: Prompt-toolkit is strong for prompts and REPL-like flows but less direct for multi-screen dashboards. Rich-only interfaces are simpler but would push more state and navigation logic into custom code.

## Decision: Rich for terminal presentation

**Rationale**: Rich provides readable terminal formatting, tables, panels, tracebacks, and styled messages, and Typer already integrates with Rich. It supports the beginner-friendly requirement by making command output easier to scan. Official package page: https://pypi.org/project/rich/

**Alternatives considered**: Plain text output was considered but would make dashboards, timelines, and suggestion reasons less readable. Textual-only rendering would not cover non-TUI command output as neatly.

## Decision: SQLite through Python `sqlite3` for local persistence

**Rationale**: SQLite is local, durable, transactional, and serverless. Python's standard `sqlite3` module provides a DB-API interface without adding an ORM dependency, and it supports the v1 scale target. Official docs: https://docs.python.org/3/library/sqlite3.html

**Alternatives considered**: JSON files are simpler initially but make relationships, filtering, duplicate detection, and history queries fragile as data grows. SQLAlchemy was considered but adds abstraction before the schema is complex enough to justify it.

## Decision: Pydantic for input and domain validation

**Rationale**: Pydantic v2 provides type-hint-driven validation, serialization, strict/lax modes, and structured error details. This helps keep CLI and TUI validation consistent while producing recoverable user-facing errors. Official docs: https://docs.pydantic.dev/

**Alternatives considered**: Dataclasses plus manual validation would reduce dependencies but duplicate validation rules across commands and screens. Full ORM model validation is unnecessary for this local-first app.

## Decision: Rule-based suggestion engine for v1

**Rationale**: The spec requires explainable suggestions based on history, open loops, due dates, stale relationships, and prior outcomes. A deterministic scoring model can produce clear reasons, is testable, and works offline.

**Alternatives considered**: ML or LLM-driven suggestions were rejected for v1 because they add hosting, privacy, cost, and explainability concerns. Manual-only reminders were rejected because they do not satisfy the suggestion requirement.

## Decision: Shared service layer for CLI and TUI

**Rationale**: Direct commands and TUI screens must behave consistently. A shared service layer prevents duplicated workflow logic and keeps tests focused on business behavior rather than terminal adapters.

**Alternatives considered**: Separate CLI and TUI implementations would be faster to prototype but likely diverge. A service-heavy architecture with many abstractions was rejected; services should stay thin and task-focused.
