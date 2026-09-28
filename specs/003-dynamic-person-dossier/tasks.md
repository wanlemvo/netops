> Historical design record; not current product instructions. See the [current README](../../README.md).

# Tasks: Dynamic Person Dossier

**Input**: Design documents from `specs/003-dynamic-person-dossier/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Included because the feature spec and plan call for unit, contract, and integration coverage.
**Implementation Focus**: Core workflows first: person creation, person overview, interaction logging, follow-up suggestions. Advanced analytics and graph/network logic are intentionally deferred.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks in the same phase because it touches different files or depends only on completed phases
- **[Story]**: Maps to user stories in `specs/003-dynamic-person-dossier/spec.md`
- Every task includes an exact repository path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the feature surface without changing behavior.

- [X] T001 Create dossier TUI module placeholder in `src/netops/tui/dossier.py`
- [X] T002 [P] Create dossier service test scaffold in `tests/unit/test_people_dossier_service.py`
- [X] T003 [P] Create dossier data contract test scaffold in `tests/contract/test_dossier_data_behavior.py`
- [X] T004 [P] Create dossier TUI flow contract test scaffold in `tests/contract/test_dossier_tui_flow.py`
- [X] T005 [P] Create dossier keyboard integration test scaffold in `tests/integration/test_dossier_keyboard_flow.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared data and service foundation needed by all dossier workflows.

**Critical**: No user story work should begin until these tasks are complete.

- [X] T006 Add optional dossier fields and `RawNoteEntry` model to `src/netops/domain/models.py`
- [X] T007 Add dossier field normalization helpers for list fields and relationship strength in `src/netops/domain/validation.py`
- [X] T008 Add SQLite migration for optional person dossier columns and `person_notes` in `src/netops/storage/migrations.py`
- [X] T009 Extend person row mapping, insert, and update behavior for dossier fields in `src/netops/storage/repositories.py`
- [X] T010 Add append-only person note repository methods in `src/netops/storage/repositories.py`
- [X] T011 Add migration compatibility tests for existing minimal people in `tests/integration/test_dossier_migration_compatibility.py`
- [X] T012 Add repository tests for dossier field persistence and person notes in `tests/unit/test_person_notes_repository.py`

**Checkpoint**: Existing people load as valid minimal dossiers and storage can persist optional fields without breaking current CLI behavior.

---

## Phase 3: User Story 1 - Add A Minimal Person (Priority: P1) MVP

**Goal**: A user can create a person with only a name from the keyboard TUI and see the new person immediately.

**Independent Test**: Open People, select `+ Add Person`, enter only a name, save, and confirm the person appears and opens as a valid dossier.

### Tests for User Story 1

- [X] T013 [P] [US1] Add unit tests for name-only creation and missing-name validation in `tests/unit/test_people_dossier_service.py`
- [X] T014 [P] [US1] Add TUI contract tests for Add Person name-only save and draft preservation in `tests/contract/test_dossier_tui_flow.py`
- [X] T015 [P] [US1] Add integration test for keyboard Add Person flow in `tests/integration/test_dossier_keyboard_flow.py`

### Implementation for User Story 1

- [X] T016 [US1] Update `PeopleService.create_person` to require only name and preserve optional dossier fields in `src/netops/services/people.py`
- [X] T017 [US1] Update `PersonFormDraft` for name-first minimal creation in `src/netops/tui/state.py`
- [X] T018 [US1] Update Add Person rendering and save/cancel actions in `src/netops/tui/screens.py`
- [X] T019 [US1] Wire successful Add Person save to refresh People List and preserve keyboard flow in `src/netops/tui/state.py`
- [X] T020 [US1] Run focused tests for person creation with `python -m pytest tests/unit/test_people_dossier_service.py tests/contract/test_dossier_tui_flow.py tests/integration/test_dossier_keyboard_flow.py`

**Checkpoint**: Person creation is independently usable and testable as the MVP.

---

## Phase 4: User Story 3 - View Structured Dossier / Person Overview (Priority: P3)

**Goal**: A user can open a person overview that reads like a structured dossier with Identity, Relationship, Personal Intelligence, Interaction, Opportunity, and Raw Notes sections.

**Independent Test**: Open any person dossier and confirm empty and populated fields render in their sections without command text or broken layout.

### Tests for User Story 3

- [X] T021 [P] [US3] Add contract tests for required dossier sections and empty placeholders in `tests/contract/test_dossier_tui_flow.py`
- [X] T022 [P] [US3] Add service tests for composing a person dossier read model in `tests/unit/test_people_dossier_service.py`
- [X] T023 [P] [US3] Add data contract tests for existing people opening as valid dossiers in `tests/contract/test_dossier_data_behavior.py`

### Implementation for User Story 3

- [X] T024 [US3] Add `PersonDossier` composition helpers with last-contact and section data in `src/netops/services/people.py`
- [X] T025 [US3] Implement dossier section view models and row builders in `src/netops/tui/dossier.py`
- [X] T026 [US3] Update `dossier_screen` to render sectioned person overview from `src/netops/tui/dossier.py` in `src/netops/tui/screens.py`
- [X] T027 [US3] Update `TuiState.open_dossier` to call service-level dossier composition in `src/netops/tui/state.py`
- [X] T028 [US3] Run focused person overview tests with `python -m pytest tests/unit/test_people_dossier_service.py tests/contract/test_dossier_tui_flow.py tests/contract/test_dossier_data_behavior.py`

**Checkpoint**: The dossier overview is useful before field editing, analytics, or network logic exists.

---

## Phase 5: User Story 5 - Track Interaction Intelligence: Interaction Logging (Priority: P5)

**Goal**: A user can log an interaction tied to a person and the dossier overview reflects recent interaction context and last contact.

**Independent Test**: Log an interaction for a person, reopen that dossier, and confirm the Interaction section shows the newest interaction date and recent notes.

### Tests for User Story 5 Interaction Logging

- [X] T029 [P] [US5] Add unit tests for last-contact derivation from interactions in `tests/unit/test_people_dossier_service.py`
- [X] T030 [P] [US5] Add integration tests for logging an interaction and refreshing dossier overview in `tests/integration/test_dossier_keyboard_flow.py`
- [X] T031 [P] [US5] Add contract tests for interaction section display in `tests/contract/test_dossier_tui_flow.py`

### Implementation for User Story 5 Interaction Logging

- [X] T032 [US5] Add interaction logging draft state and actions in `src/netops/tui/state.py`
- [X] T033 [US5] Add interaction logging screen renderer in `src/netops/tui/screens.py`
- [X] T034 [US5] Add dossier action row for `Log Interaction` in `src/netops/tui/dossier.py`
- [X] T035 [US5] Wire TUI interaction save through `InteractionService.log_interaction` in `src/netops/tui/state.py`
- [X] T036 [US5] Run focused interaction logging tests with `python -m pytest tests/unit/test_people_dossier_service.py tests/contract/test_dossier_tui_flow.py tests/integration/test_dossier_keyboard_flow.py`

**Checkpoint**: Dossiers now reflect real relationship activity, with no graph/network expansion.

---

## Phase 6: User Story 5 - Track Interaction Intelligence: Follow-Up Suggestions (Priority: P5)

**Goal**: A user can see actionable follow-up suggestions from the dossier and overview based on existing open loops and interaction history.

**Independent Test**: Create or log a follow-up, generate suggestions, and confirm relevant suggestions appear without introducing advanced analytics.

### Tests for User Story 5 Follow-Up Suggestions

- [X] T037 [P] [US5] Add suggestion service tests for open-loop and stale-contact follow-ups in `tests/unit/test_suggestion_rules.py`
- [X] T038 [P] [US5] Add dossier contract tests for Opportunity section suggestions in `tests/contract/test_dossier_tui_flow.py`
- [X] T039 [P] [US5] Add integration test for follow-up suggestion visibility after interaction logging in `tests/integration/test_suggestions.py`

### Implementation for User Story 5 Follow-Up Suggestions

- [X] T040 [US5] Keep suggestion generation rule-based and local in `src/netops/domain/suggestions.py`
- [X] T041 [US5] Add service helper for dossier-scoped suggestions in `src/netops/services/suggestions.py`
- [X] T042 [US5] Render follow-up suggestions in the dossier Opportunity section in `src/netops/tui/dossier.py`
- [X] T043 [US5] Surface top follow-up suggestions in Overview without graph analytics in `src/netops/tui/screens.py`
- [X] T044 [US5] Run focused suggestion tests with `python -m pytest tests/unit/test_suggestion_rules.py tests/integration/test_suggestions.py tests/contract/test_dossier_tui_flow.py`

**Checkpoint**: Follow-up suggestions support core workflow decisions while advanced analytics remains deferred.

---

## Phase 7: User Story 2 - Browse Grouped People List (Priority: P2)

**Goal**: A user can browse an alphabetized person index grouped under first-letter headers.

**Independent Test**: Create people with names across letters and symbols, open People List, and verify headers are visible and non-activating while person rows open dossiers.

### Tests for User Story 2

- [X] T045 [P] [US2] Add unit tests for grouped people rows and `#` fallback grouping in `tests/unit/test_people_dossier_service.py`
- [X] T046 [P] [US2] Add TUI contract tests for non-activating header rows in `tests/contract/test_dossier_tui_flow.py`
- [X] T047 [P] [US2] Add integration test for alphabetized keyboard People List navigation in `tests/integration/test_dossier_keyboard_flow.py`

### Implementation for User Story 2

- [X] T048 [US2] Add grouped directory row builder to `PeopleService` in `src/netops/services/people.py`
- [X] T049 [US2] Add header row support to People List rendering in `src/netops/tui/screens.py`
- [X] T050 [US2] Update selection movement to skip or no-op non-activating headers in `src/netops/tui/state.py`
- [X] T051 [US2] Run focused grouped list tests with `python -m pytest tests/unit/test_people_dossier_service.py tests/contract/test_dossier_tui_flow.py tests/integration/test_dossier_keyboard_flow.py`

**Checkpoint**: Person browsing scales to the 1,000-person target without needing search, graph, or network views.

---

## Phase 8: User Story 4 - Edit Profile Field By Field (Priority: P4)

**Goal**: A user can select one dossier field, edit it, and save without rewriting unrelated profile data.

**Independent Test**: Open a dossier, edit one field such as role or interests, and confirm the field updates while unrelated fields remain unchanged.

### Tests for User Story 4

- [X] T052 [P] [US4] Add service tests for editable field allowlist and unrelated-field preservation in `tests/unit/test_people_dossier_service.py`
- [X] T053 [P] [US4] Add validation tests for relationship strength and list fields in `tests/contract/test_dossier_data_behavior.py`
- [X] T054 [P] [US4] Add TUI contract tests for Edit Profile field selection and invalid draft preservation in `tests/contract/test_dossier_tui_flow.py`

### Implementation for User Story 4

- [X] T055 [US4] Add editable field metadata and single-field update method to `PeopleService` in `src/netops/services/people.py`
- [X] T056 [US4] Add edit-profile draft state and validation handling in `src/netops/tui/state.py`
- [X] T057 [US4] Add Edit Profile list and field edit renderers in `src/netops/tui/screens.py`
- [X] T058 [US4] Add `Edit Profile` action rows to dossier view models in `src/netops/tui/dossier.py`
- [X] T059 [US4] Run focused edit-profile tests with `python -m pytest tests/unit/test_people_dossier_service.py tests/contract/test_dossier_data_behavior.py tests/contract/test_dossier_tui_flow.py`

**Checkpoint**: Dossiers can grow over time through safe, focused edits.

---

## Phase 9: User Story 5 - Append Raw Notes (Priority: P5)

**Goal**: A user can append raw notes from the dossier without overwriting previous notes.

**Independent Test**: Append multiple notes to a person and confirm all previous notes remain visible in deterministic order.

### Tests for User Story 5 Raw Notes

- [X] T060 [P] [US5] Add repository tests proving raw notes append without update/delete behavior in `tests/unit/test_person_notes_repository.py`
- [X] T061 [P] [US5] Add data contract tests for raw note ordering and preservation in `tests/contract/test_dossier_data_behavior.py`
- [X] T062 [P] [US5] Add TUI contract tests for Append Raw Note validation in `tests/contract/test_dossier_tui_flow.py`

### Implementation for User Story 5 Raw Notes

- [X] T063 [US5] Add person note append/list service methods in `src/netops/services/people.py`
- [X] T064 [US5] Add raw note draft state and save handling in `src/netops/tui/state.py`
- [X] T065 [US5] Add Append Raw Note screen renderer in `src/netops/tui/screens.py`
- [X] T066 [US5] Render raw notes separately from structured sections in `src/netops/tui/dossier.py`
- [X] T067 [US5] Run focused raw-note tests with `python -m pytest tests/unit/test_person_notes_repository.py tests/contract/test_dossier_data_behavior.py tests/contract/test_dossier_tui_flow.py`

**Checkpoint**: Raw note capture is append-only and visible, with destructive note editing out of scope.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Stabilize the core dossier workflows and explicitly leave advanced analytics/network logic for later.

- [X] T068 [P] Update manual validation steps in `specs/003-dynamic-person-dossier/quickstart.md`
- [X] T069 [P] Update implementation notes in `specs/003-dynamic-person-dossier/plan.md` to mark advanced analytics and graph/network logic as deferred
- [X] T070 Verify existing direct CLI command compatibility with `python -m pytest tests/contract/test_cli_commands.py tests/integration/test_command_tui_consistency.py`
- [X] T071 Run the full regression suite with `python -m pytest`
- [X] T072 Review TUI text wrapping and clipping for long notes/lists in `src/netops/tui/screens.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories
- **US1 Person Creation (Phase 3)**: Depends on Foundational and is the MVP
- **US3 Person Overview (Phase 4)**: Depends on US1 because it needs valid people to inspect
- **US5 Interaction Logging (Phase 5)**: Depends on US3 because logged interactions must surface in the dossier overview
- **US5 Follow-Up Suggestions (Phase 6)**: Depends on US5 interaction logging and existing open-loop behavior
- **US2 Grouped People List (Phase 7)**: Depends on US1, can be done earlier if needed but is not part of the first core spine
- **US4 Edit Profile (Phase 8)**: Depends on US3 because edits refresh the dossier overview
- **US5 Raw Notes (Phase 9)**: Depends on US3 and storage foundation
- **Polish (Phase 10)**: Depends on desired story slices being complete

### Core Workflow Order

1. Person creation: Phase 3
2. Person overview: Phase 4
3. Interaction logging: Phase 5
4. Follow-up suggestions: Phase 6

### Deferred Scope

- Advanced analytics beyond rule-based suggestions are deferred.
- Graph/network visualization and relationship graph traversal are deferred.
- Bulk enrichment, scoring models, and multi-person intelligence analysis are deferred.

### Parallel Opportunities

- T002-T005 can run in parallel after T001.
- T011 and T012 can be written while T006-T010 are implemented.
- Test tasks within each user story can run in parallel before implementation.
- US2 grouped list and US4 edit profile can proceed in parallel after US3 if assigned to different implementers.
- Phase 10 documentation tasks T068 and T069 can run in parallel.

---

## Parallel Example: User Story 1

```text
Task: "Add unit tests for name-only creation and missing-name validation in tests/unit/test_people_dossier_service.py"
Task: "Add TUI contract tests for Add Person name-only save and draft preservation in tests/contract/test_dossier_tui_flow.py"
Task: "Add integration test for keyboard Add Person flow in tests/integration/test_dossier_keyboard_flow.py"
```

---

## Parallel Example: Person Overview

```text
Task: "Add contract tests for required dossier sections and empty placeholders in tests/contract/test_dossier_tui_flow.py"
Task: "Add service tests for composing a person dossier read model in tests/unit/test_people_dossier_service.py"
Task: "Add data contract tests for existing people opening as valid dossiers in tests/contract/test_dossier_data_behavior.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for minimal person creation.
3. Stop and validate `netops tui` can create a person with only a name.

### Core Spine

1. Add Phase 4 person overview.
2. Add Phase 5 interaction logging.
3. Add Phase 6 follow-up suggestions.
4. Validate the full core workflow: create person, open overview, log interaction, see suggested follow-up.

### Incremental Completion

1. Add Phase 7 grouped People List for scale and scanning.
2. Add Phase 8 field-by-field editing.
3. Add Phase 9 append-only raw notes.
4. Finish Phase 10 regression and documentation updates.

### Validation Cadence

- Run focused tests at each checkpoint.
- Run direct CLI compatibility tests before final regression.
- Run `python -m pytest` before considering the feature complete.
