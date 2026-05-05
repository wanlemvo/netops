# Contract: Keyboard Navigation

The terminal interface launched by `netops tui` must be navigable without command typing.

## Global Key Behavior

| Key | Required Behavior |
|-----|-------------------|
| Up | Move selection to the previous enabled or visible selectable row when possible |
| Down | Move selection to the next enabled or visible selectable row when possible |
| Enter | Activate the selected row if enabled |
| Escape | Go back from secondary screens; show exit confirmation on Main Menu |

## Main Menu

**Visible options**:
- Overview
- People
- Open Loops
- Exit

**Rules**:
- Up/Down changes selected menu option.
- Enter on Overview opens Overview.
- Enter on People opens People List immediately.
- Enter on Open Loops opens a navigable Open Loops screen or placeholder.
- Enter on Exit shows exit confirmation.
- Escape shows exit confirmation.

## Exit Confirmation

**Visible options**:
- Yes, exit
- No, return

**Rules**:
- Enter on Yes exits the terminal interface.
- Enter on No returns to Main Menu.
- Escape returns to Main Menu.

## Disabled Or Empty-State Options

**Rules**:
- Disabled options may be shown to explain state.
- Enter on disabled options does nothing.
- Selection may land on an empty-state row only if it is useful for visibility, but activation must be a no-op.

## Small Terminal Behavior

**Rules**:
- Text must not overlap.
- Current selection must remain visible.
- If not all rows fit, the UI must indicate that content is clipped or scrollable.
