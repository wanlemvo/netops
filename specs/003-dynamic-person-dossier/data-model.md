> Historical design record; not current product instructions. See the [current README](../../README.md).

# Data Model: Dynamic Person Dossier

## Person

Existing core record expanded with optional dossier fields.

**Existing fields preserved**: `id`, `display_name`, `given_name`, `family_name`, `primary_email`, `primary_phone`, `organization`, `tags`, `relationship_notes`, `created_at`, `updated_at`.

**New identity fields**: `alias`, `role`, `location`.

**New relationship fields**: `relationship_type`, `relationship_strength`.

**New personal intelligence fields**: `birthday`, `interests`, `communication_style`, `preferences_notes`.

**New opportunity fields**: `signals`.

**Validation rules**:

- `display_name` is required and must be non-empty after trimming.
- All new fields are optional.
- `interests` and `signals` normalize from comma-separated text or lists into trimmed lists.
- `relationship_strength` accepts `1`, `2`, `3`, `4`, `5`, `low`, `medium`, or `high`; empty input clears the field.
- Existing records without new columns or values are valid minimal dossiers.

## Person Dossier

Read model composed for the TUI.

**Fields**:

- `person`: expanded `Person`.
- `relationships`: existing relationship records.
- `open_loops`: existing open loops shown as commitments.
- `recent_interactions`: existing interaction records.
- `suggestions`: existing suggested actions.
- `evaluations`: existing evaluations.
- `raw_notes`: append-only `RawNoteEntry` records.
- `last_contact`: derived from newest interaction date, not persisted as a profile field.

## RawNoteEntry

Append-only note tied to a person and displayed separately from structured profile fields.

**Fields**:

- `id`: generated identifier.
- `person_id`: required reference to `Person`.
- `note`: required non-empty note text.
- `source`: optional source label, defaulting to the dossier interface.
- `created_at`: timestamp.

**Validation rules**:

- `note` must be non-empty after trimming.
- Updates and deletes are not exposed through the dossier TUI.
- Appending a note must preserve every previous note for the person.

## EditableField

Service-level description of one field the dossier UI can edit.

**Fields**:

- `key`: stable field identifier, such as `role` or `relationship_strength`.
- `label`: user-visible label.
- `section`: one of `Identity`, `Relationship`, `Personal Intelligence`, or `Opportunity`.
- `value_type`: `text`, `list`, `date`, or `strength`.
- `current_value`: display-ready current value.

**Validation rules**:

- Only allowlisted keys can be edited.
- Saving one field cannot mutate unrelated fields.
- Validation errors preserve the user's edit draft.

## GroupedPeopleList

View model for the People screen.

**Fields**:

- `headers`: first-letter header rows, non-selectable.
- `people`: person rows sorted alphabetically by display name.
- `add_person`: final selectable `+ Add Person` row.

**Validation rules**:

- Headers are visible but activation is a no-op.
- Names starting with non-letters are grouped under `#`.
- Empty directory shows `no people` and still exposes `+ Add Person`.

## Commitment

No new persistent entity. Existing `OpenLoop` records are interpreted as person-tied commitments in the Opportunity section.

**State transitions**:

- Existing open-loop statuses remain authoritative: `open`, `completed`, `deferred`, `closed_no_action`.
- Dossier display does not change open-loop state unless an existing open-loop action is used.
