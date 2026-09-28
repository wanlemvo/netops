# Implementation Plan: Dynamic Person Dossier

**Branch**: `003-dynamic-person-dossier` | **Date**: 2026-05-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-dynamic-person-dossier/spec.md`

## Summary

Upgrade each person from a flat contact record into a structured, editable dossier that can start with only a name and accumulate intelligence over time. The implementation will preserve the keyboard-driven TUI model from `002-keyboard-tui-nav`, keep navigation modular and screen-oriented, add optional dossier fields through additive SQLite migrations, introduce append-only raw notes, and expose field-by-field profile edits through service-level contracts instead of command-style navigation.

The terminal experience should feel like browsing a structured dossier system: grouped people index, sectioned profile views, explicit dossier actions, and focused edit screens. Direct CLI commands remain available as secondary workflows, but add/view/edit dossier behavior must be reachable through the keyboard interface without command text.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic 2.x domain models, Typer for direct CLI commands, Rich for direct CLI output, prompt_toolkit 3.x for the existing keyboard TUI  
**Storage**: Existing local SQLite database with additive migrations for optional dossier columns and append-only `person_notes`  
**Testing**: pytest with unit tests for service validation/view models, contract tests for dossier data and TUI flows, and integration tests for migration compatibility and keyboard person workflows  
**Target Platform**: Local terminal on Windows, macOS, and Linux  
**Project Type**: Existing single-package local-first CLI/TUI application  
**Performance Goals**: People List remains navigable and alphabetized for at least 1,000 people; opening a dossier uses local data and should complete without perceptible delay for normal local datasets  
**Constraints**: Preserve existing people, relationships, interactions, open loops, suggestions, and evaluations; keep dossier add/view/edit flows keyboard-driven; avoid GUI frameworks and command text for TUI navigation; raw notes are append-only through the dossier interface  
**Scale/Scope**: One local user, existing NetOps dataset, People List grouping, Dossier View, Edit Profile, Append Raw Note, service/repository/storage updates, and focused tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution remains the default placeholder template and defines no ratified principles, constraints, or governance gates. No enforceable constitution violations are present.

Post-design re-check: PASS. The design is additive, keeps existing records readable, preserves current CLI commands, and confines the new user experience to the existing keyboard TUI and service/storage layers required to support dossier fields.

## Project Structure

### Documentation (this feature)

```text
specs/003-dynamic-person-dossier/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- dossier-data-behavior.md
|   `-- dossier-tui-flow.md
`-- spec.md
```

### Source Code (repository root)

```text
pyproject.toml
src/
`-- netops/
    |-- cli.py
    |-- domain/
    |   |-- models.py              # extend Person with optional dossier fields
    |   `-- validation.py          # shared dossier field normalization where appropriate
    |-- services/
    |   |-- people.py              # minimal create, dossier read model, editable-field updates
    |   |-- interactions.py        # reused for derived last contact/recent interactions
    |   |-- open_loops.py          # reused as dossier commitments
    |   |-- suggestions.py         # reused in dossier context
    |   `-- evaluations.py         # reused in dossier context
    |-- storage/
    |   |-- migrations.py          # additive dossier columns and person_notes table
    |   `-- repositories.py        # person notes repository and expanded people mapping
    `-- tui/
        |-- app.py                 # prompt_toolkit application assembly and key bindings
        |-- state.py               # navigation stack, selected rows, edit/note drafts
        |-- screens.py             # shared screen primitives and terminal text builders
        |-- dossier.py             # dossier-specific view models, sections, rows, actions
        `-- theme.py               # dossier/terminal style tokens

tests/
|-- contract/
|   |-- test_dossier_data_behavior.py
|   `-- test_dossier_tui_flow.py
|-- integration/
|   |-- test_dossier_migration_compatibility.py
|   `-- test_dossier_keyboard_flow.py
`-- unit/
    |-- test_people_dossier_service.py
    |-- test_person_notes_repository.py
    `-- test_tui_dossier_state.py
```

**Structure Decision**: Keep the current single-package architecture and extend it along existing boundaries. Storage owns migrations and row mapping, services own dossier composition and field validation, and the TUI owns navigation state and rendering. Add one dossier-focused TUI module rather than expanding `screens.py` into a large mixed-purpose file; this keeps the dossier system maintainable while preserving the modular navigation introduced by the keyboard TUI refactor.

**Deferred Scope Decision**: Implementation should prioritize the core workflow spine: person creation, person overview, interaction logging, and rule-based follow-up suggestions. Advanced analytics, graph/network visualization, relationship graph traversal, scoring models, and bulk intelligence analysis are deferred until the core dossier workflow is stable.

## Phase 0 Research Output

Research decisions are recorded in [research.md](research.md):

- Add optional dossier fields to `people` through additive SQLite migrations.
- Store raw notes in a separate append-only `person_notes` table.
- Derive last contact from existing interactions.
- Reuse open loops as commitments in the Opportunity section.
- Use service allowlists for one-field-at-a-time profile editing.
- Build People List grouping as a service/screen view model, not persisted state.
- Render long dossier content using the existing TUI wrapping/clipping behavior.

No `NEEDS CLARIFICATION` items remain.

## Phase 1 Design Output

Design artifacts are recorded in:

- [data-model.md](data-model.md)
- [contracts/dossier-data-behavior.md](contracts/dossier-data-behavior.md)
- [contracts/dossier-tui-flow.md](contracts/dossier-tui-flow.md)
- [quickstart.md](quickstart.md)

The AGENTS context has been updated to point at this plan.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
