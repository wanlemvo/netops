> Historical design record; not current product instructions. See the [current README](../../README.md).

# Tasks: NetworkOps Person Intelligence Record

**Input**: Design documents from `specs/004-person-intelligence-record/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `docs/schema_v1.md`

**Tests**: Test tasks are included because the feature changes schema, persistence, migration behavior, long-form text handling, and user-visible workflows.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or depends only on completed foundation work
- **[Story]**: Maps task to a user story from `spec.md`
- Every task includes exact file paths

## Phase 1: Setup

**Purpose**: Prepare schema implementation context and test fixtures.

- [X] T001 Review approved V1 schema and record implementation notes in `specs/004-person-intelligence-record/tasks.md`
- [X] T002 [P] Add reusable V1 test database fixture helpers in `tests/conftest.py`
- [X] T003 [P] Add profile photo fixture asset placeholder in `assets/demo/.gitkeep`
- [X] T004 [P] Add V1 schema test module scaffold in `tests/unit/test_v1_schema_contract.py`

Implementation note: V1 is implemented additively on top of the legacy schema so existing CLI/TUI paths continue to work while new V1 repository methods and tables come online. Legacy tables are preserved; standalone `notes` is not introduced.

---

## Phase 2: Foundational

**Purpose**: Core schema, migration, domain, and repository infrastructure that blocks all user stories.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T005 Add V1 SQLite migration for people, contact_methods, interactions, interaction_people, signals, opportunities, opportunity_people, relationship_links, tags, and taggings in `src/netops/storage/migrations.py`
- [X] T006 Add migration compatibility mapping from existing people/contact/note/interaction/open-loop records into V1-compatible tables in `src/netops/storage/migrations.py`
- [X] T007 [P] Add schema contract tests for V1 tables, columns, indexes, and absence of standalone notes in `tests/unit/test_v1_schema_contract.py`
- [X] T008 [P] Add migration compatibility tests for existing dossier-era data in `tests/integration/test_v1_migration_compatibility.py`
- [X] T009 Update database initialization/version handling for V1 migrations in `src/netops/storage/database.py`
- [X] T010 Update domain models for V1 entities and join records in `src/netops/domain/models.py`
- [X] T011 Update validation helpers for UUID text IDs, date text, boolean flags, controlled text values, and multiline text preservation in `src/netops/domain/validation.py`
- [X] T012 Update repository boundaries for V1 tables without standalone notes in `src/netops/storage/repositories.py`
- [X] T013 [P] Add repository tests for UUID identity, archive fields, and relationship-link entity type validation in `tests/unit/test_repositories.py`
- [X] T014 [P] Add service-level test scaffold for V1 people records in `tests/unit/test_people_v1_service.py`
- [X] T015 Run `python -m pytest tests/unit/test_v1_schema_contract.py tests/integration/test_v1_migration_compatibility.py` and confirm expected failures before story implementation

**Checkpoint**: Foundation ready; user story implementation can begin.

---

## Phase 3: User Story 1 - Capture a complete person intelligence record (Priority: P1) MVP

**Goal**: A user can create, view, edit, save, and reopen a complete V1 person record with all approved person fields.

**Independent Test**: Create a person with V1 identity, relationship, dossier, strategic, operational, and tag data; reopen it; confirm values persist and optional missing fields are unset.

### Tests for User Story 1

- [X] T016 [P] [US1] Add contract tests for V1 person data behavior in `tests/contract/test_v1_person_data_behavior.py`
- [X] T017 [P] [US1] Add integration tests for creating, editing, reopening, and listing V1 person records in `tests/integration/test_v1_person_record_flow.py`
- [X] T018 [P] [US1] Add unit tests for people service create/update/read behavior in `tests/unit/test_people_v1_service.py`

### Implementation for User Story 1

- [X] T019 [US1] Implement Person repository create/update/read/list mapping for V1 people fields in `src/netops/storage/repositories.py`
- [X] T020 [US1] Implement PeopleService V1 create/update/dossier methods in `src/netops/services/people.py`
- [X] T021 [US1] Remove `mutual_connections` from editable/display person field definitions in `src/netops/services/people.py`
- [X] T022 [US1] Update person field validation and relationship_strength text handling in `src/netops/domain/validation.py`
- [X] T023 [US1] Update direct CLI person add/show/edit flows for approved V1 person fields in `src/netops/cli.py`
- [X] T024 [US1] Update TUI person dossier display/edit field list for approved V1 person fields in `src/netops/tui/dossier.py`
- [X] T025 [US1] Update TUI screens for unset optional V1 person fields in `src/netops/tui/screens.py`
- [X] T026 [US1] Run `python -m pytest tests/contract/test_v1_person_data_behavior.py tests/integration/test_v1_person_record_flow.py tests/unit/test_people_v1_service.py`

**Checkpoint**: MVP works independently.

---

## Phase 4: User Story 2 - Store usable contact methods and profile photos (Priority: P1)

**Goal**: A user can attach structured contact methods and a local profile photo reference to a person.

**Independent Test**: Add email, phone, LinkedIn, GitHub, other social, and a profile photo to a person; reopen the app; confirm all values remain attached to that person and missing photo files do not block access.

### Tests for User Story 2

- [X] T027 [P] [US2] Add contact method contract tests in `tests/contract/test_v1_contact_methods.py`
- [X] T028 [P] [US2] Add profile photo behavior tests in `tests/integration/test_v1_profile_photo_flow.py`
- [X] T029 [P] [US2] Add repository tests for contact_methods CRUD and normalized lookup in `tests/unit/test_repositories.py`

### Implementation for User Story 2

- [X] T030 [US2] Implement ContactMethod repository methods in `src/netops/storage/repositories.py`
- [X] T031 [US2] Add contact method service operations to `src/netops/services/people.py`
- [X] T032 [US2] Add profile photo import/reference helper behavior to `src/netops/services/people.py`
- [X] T033 [US2] Update CLI contact method add/list/delete/set-primary flows in `src/netops/cli.py`
- [X] T034 [US2] Update TUI dossier contact section and profile photo state display in `src/netops/tui/dossier.py`
- [X] T035 [US2] Update portable data path handling for profile photo asset references in `src/netops/portable.py`
- [X] T036 [US2] Run `python -m pytest tests/contract/test_v1_contact_methods.py tests/integration/test_v1_profile_photo_flow.py tests/unit/test_repositories.py`

**Checkpoint**: Contact methods and profile photos work independently.

---

## Phase 5: User Story 3 - Enter long and multiline intelligence without losing data (Priority: P1)

**Goal**: Long-form fields support pasted text, multiline input, wrapping/scrolling, save, and reload without truncation.

**Independent Test**: Paste at least 2,000 characters with line breaks into long-form fields; save and reopen; confirm the full content and formatting survive.

### Tests for User Story 3

- [X] T037 [P] [US3] Add long-form storage tests for people, interactions, signals, opportunities, and relationship links in `tests/integration/test_v1_long_form_text.py`
- [X] T038 [P] [US3] Add TUI multiline edit behavior tests in `tests/integration/test_v1_multiline_tui_flow.py`
- [X] T039 [P] [US3] Add validation tests for preserving line breaks and pasted text in `tests/unit/test_v1_text_validation.py`

### Implementation for User Story 3

- [X] T040 [US3] Update validation helpers to preserve multiline text without fixed-width truncation in `src/netops/domain/validation.py`
- [X] T041 [US3] Update repository write/read mapping for long-form TEXT fields in `src/netops/storage/repositories.py`
- [X] T042 [US3] Update TUI state handling for multiline form drafts in `src/netops/tui/state.py`
- [X] T043 [US3] Update TUI screen rendering for scrollable/wrapped long-form content in `src/netops/tui/screens.py`
- [X] T044 [US3] Update dossier long-form field rendering in `src/netops/tui/dossier.py`
- [X] T045 [US3] Run `python -m pytest tests/integration/test_v1_long_form_text.py tests/integration/test_v1_multiline_tui_flow.py tests/unit/test_v1_text_validation.py`

**Checkpoint**: Long-form content is preserved independently.

---

## Phase 6: User Story 4 - Separate people from interactions, signals, and opportunities (Priority: P2)

**Goal**: Interactions, signals, opportunities, and relationship links are separate records connected to people without creating standalone notes.

**Independent Test**: Create people, a multi-person interaction, a signal sourced from an interaction, a multi-person opportunity, and a person-to-person relationship link; confirm each object is viewable independently and linked correctly.

### Tests for User Story 4

- [X] T046 [P] [US4] Add data behavior contract tests for interactions, signals, opportunities, relationship links, and no standalone notes in `tests/contract/test_v1_relationship_entities.py`
- [X] T047 [P] [US4] Add integration tests for multi-person interactions in `tests/integration/test_v1_interaction_people_flow.py`
- [X] T048 [P] [US4] Add integration tests for signals sourced from interactions in `tests/integration/test_v1_signal_flow.py`
- [X] T049 [P] [US4] Add integration tests for multi-person opportunities and relationship links in `tests/integration/test_v1_opportunity_relationship_flow.py`

### Implementation for User Story 4

- [X] T050 [US4] Implement Interaction and InteractionPerson repositories in `src/netops/storage/repositories.py`
- [X] T051 [US4] Implement Signal repository methods in `src/netops/storage/repositories.py`
- [X] T052 [US4] Implement Opportunity and OpportunityPerson repositories in `src/netops/storage/repositories.py`
- [X] T053 [US4] Implement RelationshipLink repository methods with allowed entity type validation in `src/netops/storage/repositories.py`
- [X] T054 [US4] Update interaction service behavior for multi-person interactions in `src/netops/services/interactions.py`
- [X] T055 [US4] Add signal and opportunity service behavior in `src/netops/services/people.py`
- [X] T056 [US4] Add relationship-link service behavior in `src/netops/services/people.py`
- [X] T057 [US4] Update CLI flows for interactions, signals, opportunities, and relationship links in `src/netops/cli.py`
- [X] T058 [US4] Update TUI dossier sections for interactions, signals, opportunities, and relationship links in `src/netops/tui/dossier.py`
- [X] T059 [US4] Remove standalone note creation/editing from V1-facing CLI/TUI flows or mark legacy-only in `src/netops/cli.py`
- [X] T060 [US4] Run `python -m pytest tests/contract/test_v1_relationship_entities.py tests/integration/test_v1_interaction_people_flow.py tests/integration/test_v1_signal_flow.py tests/integration/test_v1_opportunity_relationship_flow.py`

**Checkpoint**: V1 relationship entities work independently without standalone notes.

---

## Phase 7: User Story 5 - Turn relationship data into next actions (Priority: P2)

**Goal**: Person and opportunity follow-up fields make pending relationship action visible without implementing automation or recommendations.

**Independent Test**: Add next action and follow-up dates to people and opportunities; review pending items; confirm open/pending/complete opportunity status is visible.

### Tests for User Story 5

- [X] T061 [P] [US5] Add contract tests for pending follow-up visibility in `tests/contract/test_v1_follow_up_behavior.py`
- [X] T062 [P] [US5] Add integration tests for person and opportunity follow-up review in `tests/integration/test_v1_follow_up_flow.py`
- [X] T063 [P] [US5] Add unit tests for follow-up query ordering and archived filtering in `tests/unit/test_v1_follow_up_queries.py`

### Implementation for User Story 5

- [X] T064 [US5] Implement repository queries for person and opportunity follow-ups in `src/netops/storage/repositories.py`
- [X] T065 [US5] Implement follow-up review service behavior without automation in `src/netops/services/open_loops.py`
- [X] T066 [US5] Update CLI follow-up review command output for people and opportunities in `src/netops/cli.py`
- [X] T067 [US5] Update TUI overview or dossier action section for next actions and opportunity follow-ups in `src/netops/tui/screens.py`
- [X] T068 [US5] Ensure existing rule-based suggestions do not treat V1 opportunities as AI recommendations in `src/netops/services/suggestions.py`
- [X] T069 [US5] Run `python -m pytest tests/contract/test_v1_follow_up_behavior.py tests/integration/test_v1_follow_up_flow.py tests/unit/test_v1_follow_up_queries.py`

**Checkpoint**: Relationship next actions are visible independently.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full V1 slice, update docs where implementation facts changed, and protect portability.

- [X] T070 [P] Update README V1 usage examples without adding standalone notes in `README.md`
- [X] T071 [P] Update current architecture summary to reference V1 schema docs in `docs/architecture.md`
- [X] T072 [P] Update roadmap to keep AI, semantic search, graph visualization, automation, and Solo integration in future scope in `docs/roadmap.md`
- [X] T073 [P] Add quickstart validation test coverage for `specs/004-person-intelligence-record/quickstart.md` in `tests/integration/test_v1_quickstart.py`
- [X] T074 Validate portable data contract for SQLite database and profile photo assets in `scripts/build-portable.ps1`
- [X] T075 Run full test suite with `python -m pytest`
- [X] T076 Run import/compile smoke check with `python -m compileall src`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1 MVP**: Depends on Phase 2.
- **Phase 4 US2**: Depends on Phase 2 and integrates with US1 person records.
- **Phase 5 US3**: Depends on Phase 2 and can run once long-form fields exist.
- **Phase 6 US4**: Depends on Phase 2; benefits from US1 but remains independently testable through repositories/services.
- **Phase 7 US5**: Depends on Phase 2 and uses person/opportunity follow-up fields.
- **Phase 8 Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: MVP; first story to complete.
- **US2 (P1)**: Can start after foundational schema work; uses existing person records.
- **US3 (P1)**: Can start after foundational schema work; cuts across all long-form fields.
- **US4 (P2)**: Can start after foundational schema work; provides relationship entities.
- **US5 (P2)**: Can start after person/opportunity fields exist; does not require automation.

### Parallel Opportunities

- Setup tasks T002-T004 can run in parallel.
- Foundational tests T007-T008 and model/service scaffolds T013-T014 can run in parallel after T005-T006 are drafted.
- US1 tests T016-T018 can run in parallel.
- US2 tests T027-T029 can run in parallel.
- US3 tests T037-T039 can run in parallel.
- US4 tests T046-T049 can run in parallel.
- US5 tests T061-T063 can run in parallel.
- Polish documentation tasks T070-T073 can run in parallel.

---

## Parallel Example: User Story 4

```text
Task: "Add data behavior contract tests for interactions, signals, opportunities, relationship links, and no standalone notes in tests/contract/test_v1_relationship_entities.py"
Task: "Add integration tests for multi-person interactions in tests/integration/test_v1_interaction_people_flow.py"
Task: "Add integration tests for signals sourced from interactions in tests/integration/test_v1_signal_flow.py"
Task: "Add integration tests for multi-person opportunities and relationship links in tests/integration/test_v1_opportunity_relationship_flow.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Stop and validate person creation/edit/reopen behavior.

### Incremental Delivery

1. US1 establishes the person record.
2. US2 adds structured reachability and profile photos.
3. US3 fixes the long-form text problem across the app.
4. US4 adds relationship intelligence entities and links.
5. US5 exposes relationship follow-up state.

### Guardrails

- Do not add standalone notes.
- Do not add `mutual_connections`.
- Do not implement AI, semantic search, graph visualization, automation, recommendation systems, voice interfaces, or Solo tables.
- Keep `docs/schema_v1.md` as the canonical schema source.
