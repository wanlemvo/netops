> Historical design record; not current product instructions. See the [current README](../../README.md).

# Research: Keyboard TUI Navigation

## Decision: Use prompt_toolkit 3.x for the keyboard-driven terminal interface

**Rationale**: The feature requires real terminal key handling for Up, Down, Enter, and Escape without Textual or GUI frameworks. prompt_toolkit supports full-screen terminal applications built from layouts and key bindings, matching the need for explicit selection state and keyboard-driven screens. Official documentation describes full-screen applications as composed from a layout, style, and key bindings, which fits this refactor cleanly: https://python-prompt-toolkit.readthedocs.io/en/3.0.39/pages/full_screen_apps.html

**Alternatives considered**: A raw `print` + `input` loop cannot reliably capture arrow keys and Escape across Windows, macOS, and Linux without lower-level terminal handling. Textual is rejected because the feature explicitly disallows it. Curses is less portable on Windows without extra setup and is heavier for form inputs.

## Decision: Keep Typer and direct commands, but make `netops tui` independent from command parsing

**Rationale**: Existing direct commands can remain useful as secondary workflows and are already tested. The refactor target is the terminal interface, so `netops tui` should launch a self-contained keyboard application that calls services directly rather than invoking command callbacks.

**Alternatives considered**: Removing all commands was rejected because the spec says existing direct command workflows may remain available. Reusing CLI command functions internally was rejected because it would preserve the command-parser mental model inside the UI.

## Decision: Remove Textual from the active TUI implementation and project dependencies

**Rationale**: The current Textual app is the source of the GUI-like adapter shape the user rejected. Removing it from the TUI path avoids ambiguity and ensures the implementation cannot accidentally rely on clickable or widget-centric behavior.

**Alternatives considered**: Keeping Textual installed but unused was rejected because it invites future confusion and conflicts with the feature's "no Textual" constraint. A compatibility fallback can be unnecessary once prompt_toolkit is the supported TUI path.

## Decision: Model navigation as explicit state objects

**Rationale**: The required behavior depends on deterministic state transitions: selected index changes, Enter activates selected options, Escape pops screen history or prompts for exit, disabled options do nothing, and form drafts survive validation errors. A small state layer makes those transitions testable without running a live terminal.

**Alternatives considered**: Embedding all behavior inside prompt_toolkit key handlers would be faster initially but harder to test and likely to blur rendering, input, and service calls.

## Decision: Preserve existing services, repositories, models, and database schema

**Rationale**: The feature is scoped to the interaction layer and explicitly requires preserving existing data and logic. The People List, Add Person Form, Dossier View, Overview, and Open Loops screens should call the existing service methods.

**Alternatives considered**: Creating new TUI-specific data models or storage paths was rejected because it risks breaking compatibility and duplicates behavior already covered by tests.

## Decision: Use a terminal-native cyberpunk theme through styles and text rendering

**Rationale**: The requested aesthetic can be achieved through selected-state highlighting, high-contrast colors, borders, titles, status lines, and concise terminal copy without graphical or mouse-driven elements.

**Alternatives considered**: Image-like ASCII art or heavy decorative output was rejected because it can crowd small terminals and distract from keyboard navigation.
