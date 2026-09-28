> Historical design record; not current product instructions. See the [current README](../../README.md).

# Implementation Plan: Keyboard TUI Navigation

**Branch**: `002-keyboard-tui-nav` | **Date**: 2026-05-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-keyboard-tui-nav/spec.md`

## Summary

Refactor NetOps' terminal interface from the current Textual-style screen adapter into a keyboard-driven terminal system where Up/Down changes selection, Enter activates the selected item, and Escape goes back or confirms exit from the Main Menu. The refactor will preserve the existing domain models, SQLite storage, repositories, and services, and will focus changes on `src/netops/tui/`, the `netops tui` entry path, tests, and dependency metadata.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Typer and Rich remain for direct CLI output; prompt_toolkit 3.x is added for full-screen terminal input, key bindings, layout, and form fields; Textual is removed from the TUI path and dependency list  
**Storage**: Existing local SQLite storage remains unchanged  
**Testing**: pytest with unit tests for navigation state, contract tests for keyboard behavior, and integration tests for preserving people data and service behavior  
**Target Platform**: Local terminal on Windows, macOS, and Linux  
**Project Type**: Existing single-package CLI/TUI application interaction-layer refactor  
**Performance Goals**: People List appears in under 2 seconds for 1,000 local people; keyboard selection updates without perceptible delay  
**Constraints**: No Textual or GUI frameworks; no clickable or mouse-required UI; no command typing for terminal-interface navigation; preserve existing data, models, services, and direct command workflows  
**Scale/Scope**: Main Menu, Overview, People List, Dossier View, Add Person Form, and Open Loops entry screen for the existing single-user local NetOps dataset

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The current constitution file remains the default placeholder template and defines no ratified principles, constraints, or governance gates. No enforceable constitution violations are present.

Post-design re-check: PASS. The design keeps the refactor scoped to the interaction layer, preserves existing data and domain behavior, and removes the disallowed Textual dependency from the TUI path.

## Project Structure

### Documentation (this feature)

```text
specs/002-keyboard-tui-nav/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- keyboard-navigation.md
|   `-- screen-behavior.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
pyproject.toml
src/
`-- netops/
    |-- cli.py
    |-- tui/
    |   |-- __init__.py
    |   |-- app.py              # prompt_toolkit application assembly and run loop
    |   |-- state.py            # screen stack, selection, form draft, commands
    |   |-- screens.py          # renderable screen models and text builders
    |   `-- theme.py            # cyberpunk terminal style tokens
    |-- services/               # existing services reused unchanged unless adapter needs import changes
    |-- storage/                # existing storage unchanged
    `-- domain/                 # existing domain unchanged

tests/
|-- contract/
|   |-- test_keyboard_navigation.py
|   `-- test_tui_screens.py
|-- integration/
|   |-- test_keyboard_tui_people_flow.py
|   `-- test_command_tui_consistency.py
`-- unit/
    `-- test_tui_state.py
```

**Structure Decision**: Keep the existing package and service architecture. Replace the Textual-backed TUI adapter with a small prompt_toolkit-backed interaction layer composed of state, screen rendering, keyboard bindings, and a terminal theme. Direct CLI commands remain available but are not used internally for navigation.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
