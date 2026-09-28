# Contract: Dossier TUI Flow

## Navigation contract

- Up and Down move selection among selectable rows.
- Enter activates the selected enabled row.
- Escape returns to the previous screen.
- Escape on Main Menu opens the existing exit confirmation flow.
- Enter on disabled rows, headers, empty-state rows, or unavailable options is a no-op.
- No dossier add/view/edit flow requires command text such as `netops people add`.
- Dossier screens present explicit selectable actions and sectioned content, not command prompts.
- TUI navigation state, dossier section composition, and persistence calls remain separate implementation concerns.

## People List

Opening People from Main Menu immediately displays the People List.

Rows:

- First-letter headers: non-selectable, non-activating.
- Person rows: selectable; Enter opens the person's Dossier View.
- Empty-state row: `no people`, non-activating.
- `+ Add Person`: selectable; Enter opens Add Person Form.

Ordering:

- Person rows are sorted alphabetically by display name.
- Headers appear before each letter group.
- Non-letter names are grouped under `#`.

## Add Person Form

Fields:

- `name`: required.
- Optional fields may be present but are not required.

Behavior:

- Saving with only `name` creates a valid person.
- Saving without `name` displays a validation message and preserves the current draft.
- Successful save returns to People List and the new person appears in the correct group.
- Escape leaves the form using the existing unsaved-draft behavior.

## Dossier View

The dossier displays these sections in order:

1. Identity
2. Relationship
3. Personal Intelligence
4. Interaction
5. Opportunity
6. Raw Notes

Actions:

- `Edit Profile`: opens editable field list.
- `Append Raw Note`: opens raw note append draft.
- Back option or Escape returns to People List.

Display:

- Empty optional values render as an unset/empty placeholder, not as errors.
- Long rows wrap or clip using existing terminal screen behavior.
- Raw notes are separate from structured fields.

## Edit Profile

The user selects `Edit Profile`, then selects one editable field.

Field edit behavior:

- The edit screen shows the selected field label and current value.
- User input replaces the selected structured field only.
- List fields accept comma-separated values.
- Empty input clears optional fields.
- Invalid relationship strength displays a validation message and preserves the edit draft.
- Successful save immediately refreshes the Dossier View with the updated value.

## Append Raw Note

The user selects `Append Raw Note`, enters note text, and saves.

Behavior:

- Empty note input displays a validation message and preserves the draft.
- Saving appends a new raw note row.
- Existing raw notes remain visible and unchanged.
