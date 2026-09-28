> Historical design record; not current product instructions. See the [current README](../../README.md).

# Implementation Plan: NetworkOps Person Intelligence Record

**Branch**: `004-person-intelligence-record` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/004-person-intelligence-record/spec.md`, refined by approved architecture, ADRs, data model, project audit, and schema documents.

## Summary

Implement NetworkOps V1 as a local-first Person Intelligence Record system. People remain the primary entity, with structured contact methods, multi-person interactions, signals, opportunities, and relationship links providing context around each person. The implementation will evolve the existing Python CLI/TUI application and SQLite persistence layer through additive schema work, repository/service updates, and focused tests while preserving existing local records.

The approved scope excludes standalone notes from NetOps V1. Existing note-like data must be preserved during migration, but no standalone notes entity should be added to the V1 schema. Relationship context between people must come from `relationship_links`, not duplicated freeform fields such as `mutual_connections`.

## Technical Context

**Language/Version**: Python 3.11+; current local environment may use Python 3.12.x  
**Primary Dependencies**: Typer, Rich, prompt_toolkit, Pydantic 2.x, Python standard-library `sqlite3`  
**Storage**: Local SQLite database in standard app data or portable `NETOPS_HOME/data`; profile photos stored as local files referenced by path  
**Testing**: pytest unit, integration, and contract tests  
**Target Platform**: Local Windows-first CLI/terminal app with cross-platform Python compatibility where existing project supports it  
**Project Type**: Single-package local-first CLI/TUI application  
**Performance Goals**: Person record open/save should feel immediate for normal local datasets; existing target remains usable around 1,000 people and 10,000 interactions  
**Constraints**: Local-first; single-user; no cloud dependency; preserve existing records; do not introduce standalone notes; do not implement AI, semantic search, graph visualization, automation, recommendation systems, or voice interfaces  
**Scale/Scope**: V1 schema and workflows for People, Contact Methods, Interactions, Signals, Opportunities, Relationship Links, and Tags where needed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution file is still a placeholder template and defines no ratified enforceable gates. No constitution violations are present.

Post-design re-check: PASS. The design follows the approved docs, keeps the work local-first, avoids out-of-scope systems, and preserves implementation boundaries between schema, domain, services, repositories, and CLI/TUI surfaces.

## Project Structure

### Documentation (this feature)

```text
specs/004-person-intelligence-record/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- data-behavior.md
|   `-- cli-tui-behavior.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
src/
`-- netops/
    |-- cli.py
    |-- portable.py
    |-- domain/
    |   |-- models.py
    |   |-- validation.py
    |   `-- suggestions.py
    |-- services/
    |   |-- people.py
    |   |-- interactions.py
    |   |-- open_loops.py
    |   |-- suggestions.py
    |   `-- evaluations.py
    |-- storage/
    |   |-- database.py
    |   |-- migrations.py
    |   `-- repositories.py
    `-- tui/
        |-- app.py
        |-- state.py
        |-- screens.py
        |-- dossier.py
        `-- theme.py

tests/
|-- contract/
|-- integration/
`-- unit/
```

**Structure Decision**: Keep the existing single-package architecture. Schema and persistence changes belong in `src/netops/storage/`; domain shape and validation in `src/netops/domain/`; workflow behavior in `src/netops/services/`; direct CLI and TUI surfaces adapt to the same service layer. Do not introduce a new app, server, graph database, note subsystem, or Solo module.

## Phase 0: Research Summary

Research decisions are recorded in [research.md](research.md).

Key outcomes:

- Use SQLite for V1 local-first structured storage.
- Use UUID text identifiers for true record identity.
- Keep people as the primary entity.
- Store profile photos as local assets, with only relative references in SQLite.
- Store long-form multiline values as unrestricted text.
- Use relationship links and join tables for relationship context instead of duplicating connections in person records.
- Keep standalone notes out of NetOps V1.

## Phase 1: Design Summary

Design artifacts are recorded in:

- [data-model.md](data-model.md)
- [contracts/data-behavior.md](contracts/data-behavior.md)
- [contracts/cli-tui-behavior.md](contracts/cli-tui-behavior.md)
- [quickstart.md](quickstart.md)

The canonical schema source is [../../docs/schema_v1.md](../../docs/schema_v1.md). This feature plan should not contradict that document.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
