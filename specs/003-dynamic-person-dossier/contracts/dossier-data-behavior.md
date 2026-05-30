# Contract: Dossier Data Behavior

## Compatibility

Existing local data remains readable after migration:

- Existing `people` rows become valid dossiers with empty optional fields.
- Existing `relationships`, `interactions`, `open_loops`, `suggested_actions`, and `evaluations` remain unchanged.
- Existing direct CLI commands continue to resolve people by ID, exact name, or partial name.

## Persistence contract

The migration is additive:

- Add optional profile columns to `people`.
- Add `person_notes` for append-only raw notes.
- Keep existing table names, primary keys, and foreign keys.

List fields:

- `tags`, `interests`, and `signals` persist as JSON arrays of strings.
- Invalid or missing JSON values load as empty lists only when legacy data requires tolerance.

## Field edit contract

Supported editable fields:

- `display_name`
- `alias`
- `organization`
- `role`
- `location`
- `relationship_type`
- `relationship_strength`
- `birthday`
- `interests`
- `communication_style`
- `preferences_notes`
- `signals`

Save behavior:

- One field is updated per save.
- `updated_at` changes when a profile field changes.
- Unrelated profile fields are preserved exactly.
- Unknown field keys fail validation and do not mutate the person.
- Validation failures return a user-visible message and do not mutate storage.

Normalization:

- List input splits on commas, trims whitespace, and removes empty values.
- Relationship strength preserves numeric `1` through `5` and lower-case labels `low`, `medium`, `high`.
- Empty optional field input stores `NULL` or an empty list according to field type.

## Last contact contract

`last_contact` is derived from the newest interaction for the person:

- If interactions exist, show the latest `occurred_on` date.
- If no interactions exist, show an empty/unset value.
- Editing profile fields does not update last contact.

## Raw note contract

Raw notes are append-only through dossier behavior:

- Appending creates a new `person_notes` row.
- Existing raw note rows are not updated or deleted.
- Raw notes display newest or oldest first according to the implementation choice, but ordering must be deterministic and covered by tests.

## Commitment contract

Commitments shown in the Opportunity section map to existing `OpenLoop` records:

- Open and deferred loops are active commitments.
- Completed and closed loops may be shown as historical commitments only if the screen has room or an explicit implementation choice includes them.
- Dossier work must not change existing open-loop status semantics.
