> Historical design record; not current product instructions. See the [current README](../../README.md).

# Tasks: NetOps CLI App

**Input**: Design documents from `specs/001-netops-cli-app/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Included because the plan and quickstart define pytest-based unit, integration, command contract, and TUI smoke validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: User story label for traceability.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python package, dependency metadata, and empty source/test layout.

- [X] T001 Create Python package metadata with Typer, Rich, Textual, Pydantic, pytest, and console script entry point in pyproject.toml
- [X] T002 Create package entry files in src/netops/__init__.py and src/netops/__main__.py
- [X] T003 [P] Create CLI adapter placeholder in src/netops/cli.py
- [X] T004 [P] Create TUI package placeholders in src/netops/tui/__init__.py, src/netops/tui/app.py, and src/netops/tui/screens.py
- [X] T005 [P] Create domain package placeholders in src/netops/domain/__init__.py, src/netops/domain/models.py, src/netops/domain/validation.py, and src/netops/domain/suggestions.py
- [X] T006 [P] Create storage package placeholders in src/netops/storage/__init__.py, src/netops/storage/database.py, src/netops/storage/migrations.py, and src/netops/storage/repositories.py
- [X] T007 [P] Create service package placeholders in src/netops/services/__init__.py, src/netops/services/people.py, src/netops/services/interactions.py, src/netops/services/open_loops.py, src/netops/services/suggestions.py, and src/netops/services/evaluations.py
- [X] T008 [P] Create pytest directory structure in tests/unit/, tests/integration/, and tests/contract/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core infrastructure that every user story depends on.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T009 Define shared domain enums and Pydantic base model conventions in src/netops/domain/models.py
- [X] T010 Implement user-facing validation error helpers in src/netops/domain/validation.py
- [X] T011 Implement application data path resolution and SQLite connection factory in src/netops/storage/database.py
- [X] T012 Implement SQLite migration runner and schema version tracking in src/netops/storage/migrations.py
- [X] T013 Create initial SQLite schema for people, relationships, interactions, open_loops, suggested_actions, and evaluations in src/netops/storage/migrations.py
- [X] T014 Implement repository base helpers for row mapping, transactions, and not-found handling in src/netops/storage/repositories.py
- [X] T015 Implement shared service error types and person lookup helpers in src/netops/services/people.py
- [X] T016 Wire Typer root app, global options, and `netops tui` command stub in src/netops/cli.py
- [X] T017 Wire Textual app shell and main navigation placeholders in src/netops/tui/app.py
- [X] T018 [P] Add foundational model validation tests in tests/unit/test_models.py
- [X] T019 [P] Add migration and repository smoke tests in tests/unit/test_repositories.py

**Checkpoint**: Foundation ready; user story implementation can start.

---

## Phase 3: User Story 1 - Capture People And Interactions (Priority: P1) MVP

**Goal**: A beginner user can add people, describe relationships, and log interactions with notes in command mode and the interactive menu.

**Independent Test**: Add a person, add relationship context, log an interaction with a follow-up, and verify the saved record is visible through command output and the TUI person context.

### Tests for User Story 1

- [X] T020 [P] [US1] Add CLI contract tests for `people add`, `people list`, `relationship add`, and `log` in tests/contract/test_cli_commands.py
- [X] T021 [P] [US1] Add integration test for add-person, add-relationship, log-interaction, and follow-up persistence in tests/integration/test_persistence.py
- [X] T022 [P] [US1] Add TUI smoke test for adding or viewing a person from the People screen in tests/contract/test_tui_screens.py

### Implementation for User Story 1

- [X] T023 [P] [US1] Implement Person, Relationship, Interaction, and OpenLoop models in src/netops/domain/models.py
- [X] T024 [P] [US1] Implement person and relationship repository methods in src/netops/storage/repositories.py
- [X] T025 [P] [US1] Implement interaction and open-loop repository methods in src/netops/storage/repositories.py
- [X] T026 [US1] Implement PeopleService create/list/resolve and relationship creation in src/netops/services/people.py
- [X] T027 [US1] Implement InteractionService log interaction and optional follow-up creation in src/netops/services/interactions.py
- [X] T028 [US1] Implement OpenLoopService basic create/list/close support in src/netops/services/open_loops.py
- [X] T029 [US1] Implement `netops people add`, `netops people list`, and `netops relationship add` commands in src/netops/cli.py
- [X] T030 [US1] Implement `netops log PERSON` command with prompted missing fields and validation output in src/netops/cli.py
- [X] T031 [US1] Implement People screen basic list and person context display in src/netops/tui/screens.py
- [X] T032 [US1] Connect TUI People screen to PeopleService and InteractionService in src/netops/tui/app.py
- [X] T033 [US1] Add beginner-friendly empty-state and validation messages for capture workflows in src/netops/cli.py and src/netops/tui/screens.py

**Checkpoint**: User Story 1 is fully functional and testable as the MVP.

---

## Phase 4: User Story 2 - Review Relationship Context (Priority: P2)

**Goal**: A user can navigate the overview dashboard, people directory, dossier view, and interaction timeline to understand relationship status.

**Independent Test**: Load saved people and interactions, then navigate from overview to directory, dossier, and timeline while seeing summary counts, last interaction, open loops, and evaluated outcomes when present.

### Tests for User Story 2

- [X] T034 [P] [US2] Add TUI contract tests for Overview, People Directory, Dossier, and Timeline screens in tests/contract/test_tui_screens.py
- [X] T035 [P] [US2] Add integration test for dashboard summary, directory context, dossier aggregation, and chronological timeline in tests/integration/test_command_tui_consistency.py

### Implementation for User Story 2

- [X] T036 [P] [US2] Implement read models for dashboard summaries, dossier details, and timeline entries in src/netops/domain/models.py
- [X] T037 [US2] Implement dashboard, dossier, and timeline query methods in src/netops/storage/repositories.py
- [X] T038 [US2] Implement PeopleService directory and dossier aggregation methods in src/netops/services/people.py
- [X] T039 [US2] Implement InteractionService chronological timeline query methods in src/netops/services/interactions.py
- [X] T040 [US2] Implement Overview Dashboard, People Directory, Dossier, and Timeline screen rendering in src/netops/tui/screens.py
- [X] T041 [US2] Wire TUI navigation among overview, directory, dossier, and timeline in src/netops/tui/app.py
- [X] T042 [US2] Add CLI list/detail output helpers for people, loops, and timelines in src/netops/cli.py

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Get Suggested Next Actions (Priority: P3)

**Goal**: A user can request prioritized next actions with clear reasons based on history, open loops, follow-ups, and relationship context.

**Independent Test**: Create people with overdue follow-ups, stale contact history, and no urgent actions; verify suggestions are prioritized and explain their reasons.

### Tests for User Story 3

- [X] T043 [P] [US3] Add unit tests for suggestion scoring rules in tests/unit/test_suggestion_rules.py
- [X] T044 [P] [US3] Add CLI contract tests for `netops suggest` human-readable and JSON output in tests/contract/test_cli_commands.py
- [X] T045 [P] [US3] Add integration test for overdue, stale, ignored, and empty suggestion scenarios in tests/integration/test_suggestions.py

### Implementation for User Story 3

- [X] T046 [P] [US3] Implement SuggestedAction model and scoring input types in src/netops/domain/models.py
- [X] T047 [US3] Implement deterministic suggestion scoring and reason generation in src/netops/domain/suggestions.py
- [X] T048 [US3] Implement suggested-action repository methods for storing acted-upon suggestions in src/netops/storage/repositories.py
- [X] T049 [US3] Implement SuggestionService generate, accept, ignore, and complete operations in src/netops/services/suggestions.py
- [X] T050 [US3] Implement `netops suggest` command with `--person`, `--limit`, `--include-low-priority`, and `--json` in src/netops/cli.py
- [X] T051 [US3] Implement Suggestions screen rendering and actions in src/netops/tui/screens.py
- [X] T052 [US3] Wire Suggestions screen navigation and service calls in src/netops/tui/app.py

**Checkpoint**: User Stories 1, 2, and 3 work independently.

---

## Phase 6: User Story 4 - Evaluate Action Outcomes (Priority: P4)

**Goal**: A user can evaluate completed actions and interactions so outcome history appears in dossiers and informs future suggestion rationale.

**Independent Test**: Mark a suggestion completed, record a positive, neutral, or negative outcome, and verify it appears in the dossier and is available to suggestion scoring.

### Tests for User Story 4

- [X] T053 [P] [US4] Add CLI contract tests for `netops evaluate` validation and success output in tests/contract/test_cli_commands.py
- [X] T054 [P] [US4] Add integration test for completed suggestion evaluation and dossier visibility in tests/integration/test_command_tui_consistency.py
- [X] T055 [P] [US4] Add TUI contract test for Evaluation screen save flow in tests/contract/test_tui_screens.py

### Implementation for User Story 4

- [X] T056 [P] [US4] Implement Evaluation model and outcome validation in src/netops/domain/models.py
- [X] T057 [US4] Implement evaluation repository methods in src/netops/storage/repositories.py
- [X] T058 [US4] Implement EvaluationService create/list evaluation operations in src/netops/services/evaluations.py
- [X] T059 [US4] Integrate prior outcomes into suggestion scoring rationale in src/netops/domain/suggestions.py
- [X] T060 [US4] Implement `netops evaluate` command with action, interaction, outcome, notes, and date options in src/netops/cli.py
- [X] T061 [US4] Implement Evaluation screen candidate selection and save flow in src/netops/tui/screens.py
- [X] T062 [US4] Wire Evaluation screen navigation from dossier and suggestions in src/netops/tui/app.py

**Checkpoint**: All user stories are independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improve consistency, resilience, performance, and documentation across all stories.

- [X] T063 [P] Add quickstart workflow test coverage for the documented CLI sequence in tests/integration/test_quickstart.py
- [X] T064 [P] Add storage recovery tests for missing, empty, and unreadable local data in tests/integration/test_persistence.py
- [X] T065 Add duplicate-person disambiguation behavior across CLI and TUI in src/netops/services/people.py, src/netops/cli.py, and src/netops/tui/screens.py
- [X] T066 Add future-date confirmation handling across CLI and TUI in src/netops/domain/validation.py, src/netops/cli.py, and src/netops/tui/screens.py
- [X] T067 Optimize suggestion and timeline queries for the 1,000-person and 10,000-interaction target in src/netops/storage/repositories.py
- [X] T068 Add consistent Rich formatting for tables, errors, confirmations, and empty states in src/netops/cli.py
- [X] T069 Add terminal-size fallback messaging for TUI screens in src/netops/tui/app.py and src/netops/tui/screens.py
- [X] T070 Update quickstart usage details after implementation in specs/001-netops-cli-app/quickstart.md
- [X] T071 Run full validation commands from quickstart.md and record any deviations in specs/001-netops-cli-app/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on other stories.
- **User Story 2 (P2)**: Can start after Foundational; uses data created by US1 for realistic validation but can be tested with fixtures.
- **User Story 3 (P3)**: Can start after Foundational; uses open loops and interactions but can be tested with fixtures.
- **User Story 4 (P4)**: Can start after Foundational; integrates best after US3 but can be tested against fixture suggestions and interactions.

### Within Each User Story

- Tests should be written first and fail before implementation.
- Domain models before repositories.
- Repositories before services.
- Services before CLI/TUI adapters.
- Adapter integration before checkpoint validation.

### Parallel Opportunities

- Setup placeholders T003-T008 can run in parallel.
- Foundational tests T018-T019 can run in parallel after schema/model conventions are drafted.
- Story test tasks within each story can run in parallel.
- Repository and model tasks within a story can often run in parallel if schemas are stable.
- US2, US3, and US4 can be implemented in parallel after Phase 2 by using fixtures, with integration cleanup in Phase 7.

---

## Parallel Example: User Story 1

```text
Task: "T020 [P] [US1] Add CLI contract tests for people add/list, relationship add, and log in tests/contract/test_cli_commands.py"
Task: "T021 [P] [US1] Add integration test for capture persistence in tests/integration/test_persistence.py"
Task: "T022 [P] [US1] Add TUI smoke test for People screen in tests/contract/test_tui_screens.py"
```

```text
Task: "T023 [P] [US1] Implement Person, Relationship, Interaction, and OpenLoop models in src/netops/domain/models.py"
Task: "T024 [P] [US1] Implement person and relationship repository methods in src/netops/storage/repositories.py"
Task: "T025 [P] [US1] Implement interaction and open-loop repository methods in src/netops/storage/repositories.py"
```

## Parallel Example: User Story 2

```text
Task: "T034 [P] [US2] Add TUI contract tests for Overview, People Directory, Dossier, and Timeline screens in tests/contract/test_tui_screens.py"
Task: "T035 [P] [US2] Add integration test for review context in tests/integration/test_command_tui_consistency.py"
```

## Parallel Example: User Story 3

```text
Task: "T043 [P] [US3] Add unit tests for suggestion scoring rules in tests/unit/test_suggestion_rules.py"
Task: "T044 [P] [US3] Add CLI contract tests for netops suggest in tests/contract/test_cli_commands.py"
Task: "T045 [P] [US3] Add integration test for suggestion scenarios in tests/integration/test_suggestions.py"
```

## Parallel Example: User Story 4

```text
Task: "T053 [P] [US4] Add CLI contract tests for netops evaluate in tests/contract/test_cli_commands.py"
Task: "T054 [P] [US4] Add integration test for evaluation and dossier visibility in tests/integration/test_command_tui_consistency.py"
Task: "T055 [P] [US4] Add TUI contract test for Evaluation screen save flow in tests/contract/test_tui_screens.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate by adding a person, adding relationship context, logging an interaction, and confirming persistence in command and TUI surfaces.

### Incremental Delivery

1. Setup + Foundational creates a runnable skeleton.
2. US1 delivers the capture MVP.
3. US2 adds relationship review and navigation.
4. US3 adds explainable next-action suggestions.
5. US4 closes the feedback loop with evaluations.
6. Polish hardens edge cases, performance, and docs.

### Parallel Team Strategy

After Phase 2, one implementer can own US1 while others start US2, US3, or US4 tests and fixture-backed domain/service work. Avoid concurrent edits to shared files such as src/netops/domain/models.py and src/netops/storage/repositories.py unless the team coordinates ownership by entity.

## Notes

- `[P]` tasks are intentionally limited to work that can be done in separate files or clearly separated areas.
- Each user story has its own tests, implementation tasks, and checkpoint.
- Commit after each phase or coherent task group if using the optional Spec Kit git hooks.
