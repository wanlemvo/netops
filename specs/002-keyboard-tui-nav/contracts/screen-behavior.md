> Historical design record; not current product instructions. See the [current README](../../../README.md).

# Contract: Screen Behavior

## People List

**Entry**: Main Menu -> People

**Required content**:
- Existing people from local data
- `+ Add Person`
- Empty-state row `no people` when no people exist

**Required behavior**:
- Opens immediately without a person argument.
- Up/Down moves between rows.
- Enter on a person opens Dossier View for that person.
- Enter on `+ Add Person` opens Add Person Form.
- Enter on `no people` does nothing.
- Escape returns to Main Menu.

## Dossier View

**Entry**: People List -> selected person

**Required content**:
- Person name
- Organization or relationship context when available
- Open loops
- Recent interactions
- Suggestions
- Evaluations

**Required behavior**:
- Escape returns to People List with prior selection preserved.
- No command arguments are required.
- Missing or deleted person records show a recoverable error screen.

## Add Person Form

**Entry**: People List -> `+ Add Person`

**Required fields**:
- Name
- Organization
- Tags
- Notes

**Required behavior**:
- User can enter person details inside the terminal interface.
- Save validates required name.
- Validation failure preserves all draft values and displays a correction message.
- Successful save creates a standard Person record through existing behavior.
- After save, People List appears with the new person visible.
- Escape cancels and returns to People List after confirmation if unsaved data exists.

## Overview Screen

**Entry**: Main Menu -> Overview

**Required content**:
- People count
- Recent interactions count
- Open loops count
- Overdue follow-ups count
- Due-soon follow-ups count

**Required behavior**:
- Escape returns to Main Menu.
- Display uses terminal-native selected-state styling, borders, headings, and status lines.

## Open Loops Screen

**Entry**: Main Menu -> Open Loops

**Required content**:
- Open and deferred loops when available
- Empty-state text when none exist

**Required behavior**:
- Up/Down moves selection when rows exist.
- Enter on disabled empty-state rows does nothing.
- Escape returns to Main Menu.

## Error Screen

**Entry**: Any local data load or record lookup failure

**Required content**:
- Short error summary
- Recovery options: return to Main Menu, exit

**Required behavior**:
- The interface must not crash directly to a traceback for recoverable local data failures.
