# Tasks: Keyboard TUI Navigation

**Input**: Design documents from `specs/002-keyboard-tui-nav/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Included because the plan requires pytest unit, contract, and integration coverage for navigation state, keyboard behavior, and data-preservation regressions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each interaction slice.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: User story label for traceability.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependency metadata and files for replacing the current Textual adapter with a prompt_toolkit keyboard interface.

- [X] T001 Update project dependencies by replacing `textual>=0.60` with `prompt_toolkit>=3.0` in pyproject.toml
- [X] T002 Create terminal theme module with cyberpunk style constants in src/netops/tui/theme.py
- [X] T003 [P] Create keyboard navigation contract test file tests/contract/test_keyboard_navigation.py
- [X] T004 [P] Create TUI state unit test file tests/unit/test_tui_state.py
- [X] T005 [P] Create keyboard people-flow integration test file tests/integration/test_keyboard_tui_people_flow.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define reusable interaction state and service wiring used by all screens.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T006 Define ScreenName, SelectableItem, ScreenState, NavigationResult, and PersonFormDraft models in src/netops/tui/state.py
- [X] T007 Implement navigation stack helpers for push, pop, current screen, and selection bounds in src/netops/tui/state.py
- [X] T008 Implement selection movement behavior for Up and Down, including empty and single-item screens, in src/netops/tui/state.py
- [X] T009 Implement disabled-item activation as a no-op in src/netops/tui/state.py
- [X] T010 Implement NetOps service factory for TUI reuse without CLI command callbacks in src/netops/tui/app.py
- [X] T011 Replace Textual imports and class inheritance with prompt_toolkit-compatible application scaffolding in src/netops/tui/app.py
- [X] T012 [P] Add unit tests for selection movement, disabled no-op activation, and navigation stack behavior in tests/unit/test_tui_state.py
- [X] T013 [P] Add contract tests proving no Textual imports are required by src/netops/tui/app.py and pyproject.toml in tests/contract/test_keyboard_navigation.py

**Checkpoint**: Shared state and dependency direction are ready; user story implementation can start.

---

## Phase 3: User Story 1 - Navigate With Keyboard Only (Priority: P1) MVP

**Goal**: A user can open the terminal interface and navigate with Up, Down, Enter, and Escape without command typing.

**Independent Test**: Launch the TUI state/application layer, move selection down, activate People or Overview with Enter, and use Escape to go back or confirm exit from Main Menu without command text.

### Tests for User Story 1

- [X] T014 [P] [US1] Add contract tests for Up, Down, Enter, and Escape key mapping in tests/contract/test_keyboard_navigation.py
- [X] T015 [P] [US1] Add unit tests for Main Menu options and Escape-to-exit-confirmation behavior in tests/unit/test_tui_state.py

### Implementation for User Story 1

- [X] T016 [US1] Implement Main Menu screen construction with Overview, People, Open Loops, and Exit items in src/netops/tui/screens.py
- [X] T017 [US1] Implement Enter activation for Main Menu screen targets and Exit confirmation in src/netops/tui/state.py
- [X] T018 [US1] Implement Escape behavior for secondary-screen back navigation and Main Menu exit confirmation in src/netops/tui/state.py
- [X] T019 [US1] Implement prompt_toolkit key bindings for Up, Down, Enter, and Escape in src/netops/tui/app.py
- [X] T020 [US1] Implement prompt_toolkit layout rendering of current screen title, selectable rows, selected highlight, and status line in src/netops/tui/app.py
- [X] T021 [US1] Update `netops tui` command to launch the new keyboard application without Textual fallback logic in src/netops/cli.py

**Checkpoint**: User Story 1 is functional as the MVP: keyboard-only navigation through the Main Menu and back/exit behavior.

---

## Phase 4: User Story 2 - Browse People Without CLI Arguments (Priority: P2)

**Goal**: Selecting People immediately opens a navigable People List with existing people and `+ Add Person`.

**Independent Test**: From Main Menu, select People with arrows and Enter, verify the People List opens without arguments, move through rows, open a dossier, and see `no people` plus `+ Add Person` when empty.

### Tests for User Story 2

- [X] T022 [P] [US2] Add contract tests for People List empty state, `+ Add Person`, and no-op Enter on `no people` in tests/contract/test_tui_screens.py
- [X] T023 [P] [US2] Add integration test for selecting People from Main Menu and opening a dossier from seeded people in tests/integration/test_keyboard_tui_people_flow.py

### Implementation for User Story 2

- [X] T024 [US2] Implement People List screen builder using existing PeopleService directory data in src/netops/tui/screens.py
- [X] T025 [US2] Implement empty People List rows with disabled `no people` and enabled `+ Add Person` in src/netops/tui/screens.py
- [X] T026 [US2] Implement Enter on person rows to open Dossier View with selected person payload in src/netops/tui/state.py
- [X] T027 [US2] Implement Dossier View rendering from existing PeopleService dossier data in src/netops/tui/screens.py
- [X] T028 [US2] Preserve People List selection when returning from Dossier View with Escape in src/netops/tui/state.py
- [X] T029 [US2] Add recoverable missing-person error screen transition for stale dossier selections in src/netops/tui/state.py

**Checkpoint**: User Stories 1 and 2 both work independently: People opens as a screen, not as a command parser.

---

## Phase 5: User Story 3 - Add A Person Through The UI (Priority: P3)

**Goal**: A user can select `+ Add Person`, fill a terminal form, save, and return to People List with the new person visible.

**Independent Test**: Open People List, select `+ Add Person`, submit without a name to see preserved draft validation, then enter a valid name, save, and verify the new person appears immediately.

### Tests for User Story 3

- [X] T030 [P] [US3] Add unit tests for PersonFormDraft validation and value preservation in tests/unit/test_tui_state.py
- [X] T031 [P] [US3] Add integration test for Add Person form save and same-session People List refresh in tests/integration/test_keyboard_tui_people_flow.py

### Implementation for User Story 3

- [X] T032 [US3] Implement Add Person Form screen builder with Name, Organization, Tags, Notes, Save, and Cancel rows in src/netops/tui/screens.py
- [X] T033 [US3] Implement form field editing state and draft preservation after validation failure in src/netops/tui/state.py
- [X] T034 [US3] Implement Save behavior through existing PeopleService.create_person in src/netops/tui/state.py
- [X] T035 [US3] Implement successful save transition back to refreshed People List with the new person visible in src/netops/tui/state.py
- [X] T036 [US3] Implement Escape/cancel behavior for Add Person Form, including confirmation when unsaved draft data exists, in src/netops/tui/state.py
- [X] T037 [US3] Wire prompt_toolkit input buffers or field handling for Add Person Form in src/netops/tui/app.py

**Checkpoint**: User Stories 1, 2, and 3 work independently, including UI-driven person creation.

---

## Phase 6: User Story 4 - See A Terminal-Styled Overview (Priority: P4)

**Goal**: A user can open an Overview screen with existing NetOps summary data and terminal-forward styling.

**Independent Test**: Select Overview from Main Menu, confirm summary counts render with cyberpunk terminal styling and Escape returns to Main Menu.

### Tests for User Story 4

- [X] T038 [P] [US4] Add contract tests for Overview content and Escape return behavior in tests/contract/test_tui_screens.py
- [X] T039 [P] [US4] Add unit tests for small-terminal clipping or scroll indicator decisions in tests/unit/test_tui_state.py

### Implementation for User Story 4

- [X] T040 [US4] Implement Overview screen builder using existing PeopleService dashboard data in src/netops/tui/screens.py
- [X] T041 [US4] Implement Open Loops screen builder with existing OpenLoopService data and disabled empty-state rows in src/netops/tui/screens.py
- [X] T042 [US4] Apply cyberpunk terminal style tokens to selected rows, headings, borders, and status text in src/netops/tui/theme.py and src/netops/tui/app.py
- [X] T043 [US4] Implement small-terminal visible-selection clipping or scroll indicator logic in src/netops/tui/screens.py
- [X] T044 [US4] Add recoverable local data load error screen rendering and actions in src/netops/tui/screens.py and src/netops/tui/state.py

**Checkpoint**: All required screens are reachable and styled through keyboard navigation.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Keep existing behavior intact, remove obsolete Textual assumptions, and validate the quickstart.

- [X] T045 [P] Update existing TUI tests to target new screen/state helpers instead of Rich table-only render helpers in tests/contract/test_tui_screens.py
- [X] T046 [P] Add regression test that direct commands still work after removing Textual dependency in tests/contract/test_cli_commands.py
- [X] T047 Remove obsolete Textual-specific fallback code and exports from src/netops/tui/__init__.py and src/netops/tui/app.py
- [X] T048 Verify existing domain, storage, services, and migrations remain unchanged except imports required by the TUI adapter in src/netops/domain/, src/netops/storage/, and src/netops/services/
- [X] T049 Update specs/002-keyboard-tui-nav/quickstart.md with final run commands and any dependency notes after implementation
- [X] T050 Run `python -m pytest` and record validation result in specs/002-keyboard-tui-nav/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on other stories.
- **User Story 2 (P2)**: Depends on US1 navigation primitives and can use existing fixtures for people data.
- **User Story 3 (P3)**: Depends on US2 People List entry point and uses existing PeopleService behavior.
- **User Story 4 (P4)**: Depends on US1 navigation primitives and can be implemented independently from US2/US3 aside from shared screen rendering.

### Within Each User Story

- Tests should be written first and fail before implementation.
- State transitions before prompt_toolkit key bindings where practical.
- Screen builders before application rendering.
- Existing services should be called directly, not through CLI command callbacks.
- Story checkpoint validation should happen before moving to the next priority.

### Parallel Opportunities

- Setup test-file creation tasks T003-T005 can run in parallel.
- Foundational tests T012-T013 can run in parallel after state model names are chosen.
- Each user story's test tasks can run in parallel.
- Overview/Open Loops rendering in US4 can proceed while US3 form behavior is being implemented if `src/netops/tui/screens.py` ownership is coordinated.
- Polish regression tests T045-T046 can run in parallel.

---

## Parallel Example: User Story 1

```text
Task: "T014 [P] [US1] Add contract tests for Up, Down, Enter, and Escape key mapping in tests/contract/test_keyboard_navigation.py"
Task: "T015 [P] [US1] Add unit tests for Main Menu options and Escape-to-exit-confirmation behavior in tests/unit/test_tui_state.py"
```

## Parallel Example: User Story 2

```text
Task: "T022 [P] [US2] Add contract tests for People List empty state, + Add Person, and no-op Enter on no people in tests/contract/test_tui_screens.py"
Task: "T023 [P] [US2] Add integration test for selecting People and opening a dossier in tests/integration/test_keyboard_tui_people_flow.py"
```

## Parallel Example: User Story 3

```text
Task: "T030 [P] [US3] Add unit tests for PersonFormDraft validation and value preservation in tests/unit/test_tui_state.py"
Task: "T031 [P] [US3] Add integration test for Add Person save and People List refresh in tests/integration/test_keyboard_tui_people_flow.py"
```

## Parallel Example: User Story 4

```text
Task: "T038 [P] [US4] Add contract tests for Overview content and Escape return behavior in tests/contract/test_tui_screens.py"
Task: "T039 [P] [US4] Add unit tests for small-terminal clipping or scroll indicator decisions in tests/unit/test_tui_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational state and prompt_toolkit scaffolding.
3. Complete Phase 3: User Story 1.
4. Stop and validate that `netops tui` opens a keyboard-driven Main Menu and supports Up, Down, Enter, and Escape without command text.

### Incremental Delivery

1. US1 delivers keyboard-only navigation.
2. US2 fixes People as a real screen with list, dossier, empty state, and `+ Add Person` entry.
3. US3 adds UI-driven person creation.
4. US4 adds terminal-styled Overview, Open Loops, small-terminal handling, and recoverable error screens.
5. Polish removes old Textual assumptions and validates regressions.

### Parallel Team Strategy

After Phase 2, one implementer should own `src/netops/tui/state.py` while another owns `src/netops/tui/screens.py` tests and screen builders. Coordinate edits to `src/netops/tui/app.py`, because prompt_toolkit key bindings and layout assembly are a shared integration point.

## Notes

- This feature intentionally should not change SQLite schema, domain models, or business services unless an adapter import requires it.
- `[P]` tasks are marked only where file ownership is separate enough for parallel work.
- Direct CLI command behavior must remain available, but the TUI must not call command callbacks internally.
