> Historical design record; not current product instructions. See the [current README](../../README.md).

# Quickstart: Keyboard TUI Navigation

## Setup

```powershell
python -m pip install -e ".[dev]"
```

## Launch The Keyboard UI

```powershell
netops tui
```

Expected result: the Main Menu opens in a terminal-native view. No command prompt is required for navigation.

## Keyboard Smoke Flow

1. Press Down to move from Overview to People.
2. Press Enter.
3. Confirm the People List opens immediately.
4. If there are no people, confirm the screen shows `no people` and `+ Add Person`.
5. Select `+ Add Person` and press Enter.
6. Enter a name and save.
7. Confirm the People List returns and the new person is visible.
8. Select the person and press Enter.
9. Confirm the Dossier View opens.
10. Press Escape to return to People List.
11. Press Escape to return to Main Menu.
12. Press Escape on Main Menu and confirm exit.

## Regression Checks

Direct commands should still work:

```powershell
netops people list
netops suggest
python -m pytest
```

Expected result: existing persisted data remains readable, direct commands still execute, and tests pass.

## Validation Notes

- 2026-05-05: `python -m pip install -e ".[dev]"` installed the prompt_toolkit-based editable package.
- 2026-05-05: `python -m pytest` passed with 39 tests.
