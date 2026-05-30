# Quickstart: Dynamic Person Dossier

## Install

```powershell
python -m pip install -e ".[dev]"
```

## Run the TUI

```powershell
netops tui
```

## Manual flow

1. Open `People` from the Main Menu with arrow keys and Enter.
2. Select `+ Add Person`.
3. Enter only a name and save.
4. Confirm the person appears in the alphabetized People List under the correct letter header.
5. Open the person dossier.
6. Confirm the dossier shows Identity, Relationship, Personal Intelligence, Interaction, Opportunity, and Raw Notes.
7. Select `Edit Profile`.
8. Edit one field, such as `role`, `relationship_strength`, or `interests`.
9. Confirm the dossier refreshes immediately and unrelated fields are unchanged.
10. Select `Log Interaction`, enter notes, and optionally enter a follow-up.
11. Confirm the dossier Interaction section shows the logged interaction.
12. Confirm the Opportunity section shows a rule-based follow-up suggestion when a follow-up exists.
13. Append a raw note and confirm earlier notes remain visible.

## Regression checks

```powershell
python -m pytest
```

Expected focus areas:

- Minimal person creation still works.
- Existing people migrate into valid dossiers.
- People List is grouped and keyboard navigable.
- Relationship strength rejects invalid values.
- Raw notes append without replacing older notes.
- Existing CLI commands and open-loop behavior still pass current tests.

## Deferred scope

- Advanced analytics beyond rule-based follow-up suggestions.
- Graph or network visualization.
- Relationship graph traversal and scoring models.
