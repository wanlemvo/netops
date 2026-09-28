> Historical design record; not current product instructions. See the [current README](../../README.md).

# Data Model: Keyboard TUI Navigation

This feature does not add persistent business entities. It adds transient interaction-layer state while reusing existing NetOps records.

## Screen

Represents the current visible terminal state.

**Fields**:
- `name`: one of `main_menu`, `overview`, `people_list`, `dossier`, `add_person_form`, `open_loops`, `error`, or `exit_confirm`
- `title`: display title
- `items`: selectable options or rows
- `selected_index`: active option index
- `payload`: optional screen-specific context, such as selected person id or error message

**Relationships**:
- Stored in the Navigation Stack
- May reference Existing NetOps Records by id

**Validation rules**:
- `selected_index` must always point to a selectable item when selectable items exist.
- Empty-state-only items can be visible but disabled.
- Pressing Enter on disabled items has no side effect.

## Selectable Item

Represents a highlighted menu option or row.

**Fields**:
- `label`: visible text
- `kind`: action type, such as `open_screen`, `open_dossier`, `open_form`, `save_form`, `confirm_exit`, `cancel`, or `noop`
- `enabled`: whether Enter can activate it
- `target`: optional target screen, person id, or action identifier
- `hint`: optional status text

**Relationships**:
- Belongs to a Screen
- May reference Existing NetOps Records

**Validation rules**:
- Disabled items must not change state when activated.
- Visible empty-state labels such as `no people` should be disabled.

## Navigation Stack

Represents screen history for Escape behavior.

**Fields**:
- `screens`: ordered list of prior screens
- `current`: current screen
- `exit_requested`: whether the exit confirmation screen is active

**State transitions**:
- Main Menu + Enter on option -> push target screen
- Secondary screen + Escape -> pop previous screen
- Main Menu + Escape -> show exit confirmation
- Exit confirmation + confirm -> close interface
- Exit confirmation + cancel/Escape -> return to Main Menu

**Validation rules**:
- Escape on Main Menu must not close immediately.
- Escape on Main Menu must show confirmation first.

## Person Form Draft

Represents in-progress Add Person values.

**Fields**:
- `name`: required before save
- `email`: optional
- `phone`: optional
- `organization`: optional
- `tags`: optional
- `notes`: optional
- `active_field`: field currently receiving input
- `validation_message`: most recent validation message, if any

**Relationships**:
- Used only by Add Person Form
- Saves through existing PeopleService behavior

**Validation rules**:
- Missing required name keeps the user on the form.
- Validation errors preserve all entered fields.
- Draft is discarded only after successful save, explicit cancel, or interface exit.

## Existing NetOps Records

The TUI reuses these existing records without schema changes:
- Person
- Relationship
- Interaction
- Open Loop
- Suggested Action
- Evaluation

**Validation rules**:
- Existing persisted records must remain readable.
- Add Person Form must create standard Person records through existing service logic.
