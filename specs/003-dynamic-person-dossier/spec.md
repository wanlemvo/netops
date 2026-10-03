> Historical design record; not current product instructions. See the [current README](../../README.md).

# Feature Specification: Dynamic Person Dossier

**Feature Branch**: `003-dynamic-person-dossier`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Feature: Dynamic Person Dossier System. Goal: Upgrade the existing person model into a structured, editable intelligence dossier. Each person is not a static record, but a dynamic profile that can be expanded and edited over time. Add Person only requires name; all other fields optional. User can update any field at any time from dossier view with field-by-field editing. Data structure includes Identity, Relationship, Personal Intelligence, Interaction, and Opportunity sections. People List alphabetized by first letter and grouped under letter headers. Dossier View displays structured sections and raw notes separately. Edit flow: user selects Edit Profile, chooses a field, enters new value, value updates immediately. Must remain keyboard-driven, no command-based navigation, no GUI frameworks, integrate with existing TUI. Success: add minimal person, expand profile later, edit any field safely, dossier displays structured and raw information cleanly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add A Minimal Person (Priority: P1)

A user can add a person with only a name and return later to enrich the profile without being forced to fill optional dossier fields up front.

**Why this priority**: Fast capture is the entry point for the whole dossier system. If adding a person is heavy, users will avoid recording new contacts.

**Independent Test**: Can be fully tested by opening Add Person from the keyboard-driven People flow, entering only a name, saving, and confirming the person appears in the People List and Dossier View.

**Acceptance Scenarios**:

1. **Given** the Add Person form is open, **When** the user enters only a name and saves, **Then** the person is created successfully.
2. **Given** the Add Person form is open, **When** the user attempts to save without a name, **Then** the user sees a validation message and remains in the form.
3. **Given** a minimal person was created, **When** the user opens that person's dossier, **Then** required and empty optional sections are displayed cleanly.

---

### User Story 2 - Browse Grouped People List (Priority: P2)

A user can browse people alphabetically under letter headers so a growing contact list remains scannable from the keyboard-driven terminal interface.

**Why this priority**: A dossier system depends on finding the right person quickly as the local network grows.

**Independent Test**: Can be fully tested by creating people whose names start with different letters, opening People List, and confirming alphabetical grouping under first-letter headers while preserving arrow-key selection.

**Acceptance Scenarios**:

1. **Given** people exist with names starting with different letters, **When** the user opens People List, **Then** people are sorted alphabetically and grouped under letter headers.
2. **Given** a letter header is visible, **When** the user presses Enter on it, **Then** no profile opens because headers are not editable person rows.
3. **Given** a person row is selected, **When** the user presses Enter, **Then** that person's dossier opens.

---

### User Story 3 - View Structured Dossier (Priority: P3)

A user can open a dossier and see information grouped into Identity, Relationship, Personal Intelligence, Interaction, and Opportunity sections, with raw notes shown separately.

**Why this priority**: Structured display turns a person record into an intelligence dossier rather than a flat note.

**Independent Test**: Can be fully tested by opening a person with populated and empty fields and confirming each dossier section appears with readable values or empty-state placeholders.

**Acceptance Scenarios**:

1. **Given** a person has identity, relationship, intelligence, interaction, and opportunity data, **When** the dossier opens, **Then** each section shows the relevant fields under its section heading.
2. **Given** a person has raw notes, **When** the dossier opens, **Then** raw notes appear separately from structured fields.
3. **Given** optional fields are empty, **When** the dossier opens, **Then** the dossier still shows the section cleanly without broken layout or misleading values.

---

### User Story 4 - Edit Profile Field By Field (Priority: P4)

A user can select Edit Profile from a dossier, choose one field, enter a new value, and have that field update immediately without rewriting the whole dossier.

**Why this priority**: The dossier must grow over time through small, low-friction edits during real relationship work.

**Independent Test**: Can be fully tested by selecting Edit Profile from a dossier, changing one field such as role or relationship strength, saving, and confirming the updated value appears immediately while other fields remain unchanged.

**Acceptance Scenarios**:

1. **Given** a dossier is open, **When** the user selects Edit Profile, **Then** the user sees a navigable list of editable fields.
2. **Given** an editable field is selected, **When** the user enters a new value, **Then** that value is saved to the profile immediately after confirmation or save.
3. **Given** one field is edited, **When** the dossier refreshes, **Then** the edited value appears and unrelated fields are preserved.
4. **Given** the user edits list-style fields such as interests or signals, **When** the value is saved, **Then** the list is displayed cleanly in the relevant dossier section.

---

### User Story 5 - Track Interaction Intelligence (Priority: P5)

A user can keep append-only raw notes, see last contact updated from interactions, and track opportunity signals and commitments tied to a person.

**Why this priority**: The dossier becomes useful when it captures evolving context, not just static profile facts.

**Independent Test**: Can be fully tested by adding notes or interactions for a person, confirming last contact updates, appending raw notes without overwriting prior notes, and viewing commitments/signals in the Opportunity section.

**Acceptance Scenarios**:

1. **Given** a person has interactions, **When** a newer interaction is logged, **Then** the dossier's last contact reflects the newest interaction date.
2. **Given** raw notes already exist, **When** the user appends a new raw note, **Then** existing notes remain visible and the new note is added after prior notes.
3. **Given** a person has opportunity signals or commitments, **When** the dossier opens, **Then** those items appear in the Opportunity section.

### Edge Cases

- What happens when a person has only a name and no other dossier data?
- How does alphabetical grouping handle names that start with numbers, symbols, or whitespace?
- How does editing handle invalid relationship strength values?
- How does editing handle list fields when the user enters comma-separated values or leaves the field empty?
- How are raw notes protected from accidental full replacement?
- What happens when a selected editable field no longer exists because the profile changed during navigation?
- How does the dossier display very long notes or long lists in the keyboard-driven terminal interface?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Add Person MUST require only name.
- **FR-002**: Add Person MUST allow all other dossier fields to be left empty.
- **FR-003**: The People List MUST sort people alphabetically by displayed name.
- **FR-004**: The People List MUST group people under first-letter headers.
- **FR-005**: Letter headers in the People List MUST be non-activating rows.
- **FR-006**: The Dossier View MUST display Identity, Relationship, Personal Intelligence, Interaction, and Opportunity sections.
- **FR-007**: The Identity section MUST support name, alias, organization, role, and location.
- **FR-008**: The Relationship section MUST support relationship type and relationship strength.
- **FR-009**: Relationship strength MUST support either a 1-5 value or low, medium, high labels while preserving the user-visible meaning.
- **FR-010**: The Personal Intelligence section MUST support birthday, interests, and preferences.
- **FR-011**: Interests MUST support multiple values.
- **FR-012**: Preferences MUST support communication style and freeform notes.
- **FR-013**: The Interaction section MUST show last contact when interaction history is available.
- **FR-014**: Last contact MUST update from the latest logged interaction for the person.
- **FR-015**: Raw notes MUST be displayed separately from structured dossier sections.
- **FR-016**: Raw notes MUST be append-only through the dossier interface.
- **FR-017**: The Opportunity section MUST support signals and commitments tied to a person.
- **FR-018**: Signals MUST support multiple values.
- **FR-019**: Commitments MUST be shown as person-tied tasks or follow-ups without breaking existing open-loop behavior.
- **FR-020**: Dossier View MUST include an Edit Profile option.
- **FR-021**: Edit Profile MUST present a keyboard-navigable list of editable fields.
- **FR-022**: Users MUST be able to edit one selected field at a time without rewriting the full profile.
- **FR-023**: Saving a field edit MUST update that field immediately and preserve unrelated fields.
- **FR-024**: Invalid field values MUST show a clear validation message and preserve the user's current edit draft.
- **FR-025**: The full dossier system MUST remain keyboard-driven using the existing terminal navigation model.
- **FR-026**: No command-based navigation MUST be required to add, view, or edit dossier fields.
- **FR-027**: The feature MUST integrate with the existing terminal UI rather than introducing a separate interface.
- **FR-028**: Existing people, relationships, interactions, open loops, suggestions, and evaluations MUST remain readable after the dossier upgrade.
- **FR-029**: Existing minimal person records MUST be migrated or interpreted as valid dossiers with empty optional fields.
- **FR-030**: The dossier display MUST handle long notes and lists without overlapping terminal text.

### Key Entities *(include if feature involves data)*

- **Person Dossier**: Expanded person profile containing structured sections, raw notes, and derived interaction context.
- **Identity Section**: Name, alias, organization, role, and location.
- **Relationship Section**: Relationship type and relationship strength.
- **Personal Intelligence Section**: Birthday, interests, and preferences.
- **Interaction Section**: Last contact and append-only raw notes.
- **Opportunity Section**: Signals and commitments associated with the person.
- **Editable Field**: A single dossier field that can be selected, edited, validated, and saved without changing unrelated fields.
- **Raw Note Entry**: Append-only note text tied to a person and displayed separately from structured dossier fields.
- **Commitment**: A person-tied task or follow-up that appears in the dossier and remains compatible with existing open-loop behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can create a new person by entering only a name in under 30 seconds.
- **SC-002**: A user can open a dossier and identify all five structured sections within 5 seconds.
- **SC-003**: A user can edit any single supported profile field from the dossier in under 60 seconds without using command navigation.
- **SC-004**: Editing one field preserves 100% of unrelated profile fields in validation tests.
- **SC-005**: Existing minimal people records open as valid dossiers with no data loss.
- **SC-006**: People List remains navigable and alphabetized for at least 1,000 people.
- **SC-007**: Raw note append operations preserve prior notes in 100% of tested append scenarios.

## Assumptions

- The existing keyboard-driven terminal navigation remains the primary interaction model.
- Direct CLI commands can continue to exist, but dossier creation and editing must be possible without using command navigation.
- Existing person records may not have all new fields; missing optional fields should display as empty or unset values.
- Relationship strength can accept either numeric or label input, with validation normalizing display consistently.
- Commitments should reuse or remain compatible with existing open-loop/follow-up concepts.
- Raw notes are intentionally append-only from the dossier interface; administrative cleanup or deletion is out of scope for this feature.
- Long notes and lists should be readable through wrapping, clipping, or scrolling behavior consistent with the existing terminal UI.
