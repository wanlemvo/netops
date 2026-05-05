# Feature Specification: Keyboard TUI Navigation

**Feature Branch**: `002-keyboard-tui-nav`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Feature: Navigation System Refactor (Keyboard-Driven Terminal UI). Goal: Replace the current command-based and incorrect UI with a keyboard-driven terminal interface using arrow keys and enter. Core Problem: The current system behaves like a command parser or GUI-like TUI. This is incorrect. Required Behavior: Up/Down arrows move selection, Enter selects option, Escape goes back, no command typing required for navigation. Implement Main Menu, People List, Dossier View, Add Person Form, Overview Screen. Opening People immediately shows list, no CLI arguments required, supports arrow navigation, includes '+ Add Person'. Do not require commands like 'netops people add' for navigation. Terminal-based, no clickable UI, cyberpunk / terminal aesthetic. Preserve existing data and logic, do not break existing models, focus only on interaction layer."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate With Keyboard Only (Priority: P1)

A user can open the terminal interface and move through the application using Up, Down, Enter, and Escape without typing navigation commands.

**Why this priority**: This fixes the core interaction problem. If users still need to type commands to move around the interface, the feature has failed.

**Independent Test**: Can be fully tested by launching the terminal interface, moving the selection with arrow keys, selecting menu items with Enter, and returning with Escape without typing any command text.

**Acceptance Scenarios**:

1. **Given** the terminal interface is open on the main menu, **When** the user presses Down, **Then** the selected menu item moves to the next option.
2. **Given** a menu option is selected, **When** the user presses Enter, **Then** the matching screen opens.
3. **Given** the user is on a secondary screen, **When** the user presses Escape, **Then** the previous screen is restored.
4. **Given** the user is navigating screens, **When** they do not type command text, **Then** all navigation remains possible through keyboard selection alone.

---

### User Story 2 - Browse People Without CLI Arguments (Priority: P2)

A user can choose People from the main menu and immediately see a navigable people list, including an option to add a new person.

**Why this priority**: The People screen is the most visible broken workflow because it currently behaves like it expects command input instead of opening a usable screen.

**Independent Test**: Can be fully tested by opening the terminal interface, selecting People, confirming the list appears immediately, moving through people with arrows, opening a dossier with Enter, and selecting "+ Add Person".

**Acceptance Scenarios**:

1. **Given** the main menu is open, **When** the user selects People, **Then** the People List screen opens immediately without asking for a command argument.
2. **Given** the People List screen is open, **When** people exist, **Then** the user can move through people using Up and Down.
3. **Given** the People List screen is open, **When** the user selects a person and presses Enter, **Then** that person's dossier opens.
4. **Given** the People List screen is open, **When** the user selects "+ Add Person" and presses Enter, **Then** the Add Person Form opens.

---

### User Story 3 - Add A Person Through The UI (Priority: P3)

A user can add a person from the terminal interface without leaving the navigation flow or running a separate command.

**Why this priority**: The navigation refactor must make core data entry reachable from the UI, not only from direct commands.

**Independent Test**: Can be fully tested by selecting "+ Add Person", entering required person details in the form, saving, and returning to the People List with the new person visible.

**Acceptance Scenarios**:

1. **Given** the Add Person Form is open, **When** the user enters a valid name and saves, **Then** the new person is stored using existing people data behavior.
2. **Given** the Add Person Form is open, **When** required information is missing, **Then** the user sees a clear validation message and remains in the form.
3. **Given** a person is saved from the form, **When** the People List is shown again, **Then** the new person appears without requiring a restart.

---

### User Story 4 - See A Terminal-Styled Overview (Priority: P4)

A user can view an Overview screen from the main menu that feels like a keyboard-driven terminal system and summarizes current NetOps state.

**Why this priority**: The overview anchors the application and confirms the new interface style is a coherent terminal experience rather than a command parser.

**Independent Test**: Can be fully tested by selecting Overview from the main menu and confirming the screen shows relationship summary information with keyboard-driven navigation back to the menu.

**Acceptance Scenarios**:

1. **Given** the main menu is open, **When** the user selects Overview, **Then** the Overview screen shows summary information from existing data.
2. **Given** the Overview screen is open, **When** the user presses Escape, **Then** the main menu returns.
3. **Given** the Overview screen is shown, **When** the user inspects the visual style, **Then** it uses a terminal-forward aesthetic with text selection, borders, highlights, or status lines rather than clickable controls.

### Edge Cases

- When the People List is opened and no people exist, the screen shows an empty list state with the text "no people" and still shows "+ Add Person" as a selectable option.
- When Escape is pressed on the Main Menu, the system asks the user to confirm whether they want to exit; if confirmed, the terminal interface closes.
- When Enter is pressed on a disabled, unavailable, or empty-state-only option, the interface does nothing and remains on the same screen.
- When the terminal window is too small to show all menu options, the interface keeps the current selection visible and provides a simple scroll or clipped-list indicator rather than overlapping text.
- When Add Person validation fails, the form keeps all partially entered values and highlights or explains the field that needs correction.
- When existing local data cannot be loaded, the interface shows a recoverable error screen with an option to return to the Main Menu or exit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The terminal interface MUST support keyboard-only navigation where Up and Down move the active selection.
- **FR-002**: The terminal interface MUST use Enter to activate the currently selected option.
- **FR-003**: The terminal interface MUST use Escape to return to the previous screen when a previous screen exists.
- **FR-004**: The terminal interface MUST NOT require users to type command names, subcommands, or command arguments for navigation.
- **FR-005**: The terminal interface MUST provide a Main Menu with at least Overview, People, and Open Loops options, plus any other existing major NetOps sections that remain available.
- **FR-006**: Selecting People from the Main Menu MUST immediately open a People List screen without requiring a person argument or command-style input.
- **FR-007**: The People List screen MUST show existing people from the current local data store.
- **FR-008**: The People List screen MUST include a selectable "+ Add Person" option.
- **FR-009**: The People List screen MUST allow arrow-key selection across people and "+ Add Person".
- **FR-010**: Pressing Enter on a person in the People List MUST open that person's dossier.
- **FR-011**: Pressing Enter on "+ Add Person" MUST open the Add Person Form.
- **FR-012**: The Add Person Form MUST allow users to enter and save at least the required person information supported by existing people records.
- **FR-013**: The Add Person Form MUST validate required fields and keep the user in the form when validation fails.
- **FR-014**: Successfully saving a person from the Add Person Form MUST use existing data and business behavior so existing models and persisted records remain compatible.
- **FR-015**: The Dossier View MUST show the selected person's existing relationship context, open loops, recent interactions, suggestions, and evaluations when available.
- **FR-016**: The Overview Screen MUST show existing summary information such as people count, recent interactions, open loops, overdue follow-ups, and due-soon follow-ups when available.
- **FR-017**: The refactor MUST preserve existing data, storage compatibility, and domain behavior.
- **FR-018**: The refactor MUST be limited to the user interaction layer unless a small adapter change is required to reuse existing behavior.
- **FR-019**: The terminal interface MUST avoid mouse, pointer, or clickable interaction as a required navigation mechanism.
- **FR-020**: The interface MUST present a terminal-forward visual style with clear selected-state highlighting and a cyberpunk-inspired feel.
- **FR-021**: Existing direct command workflows MAY remain available, but the terminal interface MUST NOT depend on them for internal navigation.
- **FR-022**: Pressing Escape on the Main Menu MUST show an exit confirmation before closing the terminal interface.
- **FR-023**: The People List empty state MUST display "no people" and keep "+ Add Person" selectable.
- **FR-024**: Pressing Enter on disabled, unavailable, or empty-state-only options MUST leave the user on the current screen without side effects.
- **FR-025**: The interface MUST prevent text overlap in small terminal windows by keeping selected content visible and indicating when content is clipped or scrollable.
- **FR-026**: Add Person validation errors MUST preserve all entered form values until the user saves, cancels, or exits.
- **FR-027**: Local data load failures MUST be shown as recoverable interface errors rather than uncaught crashes.

### Key Entities *(include if feature involves data)*

- **Screen**: A distinct terminal interface state such as Main Menu, People List, Dossier View, Add Person Form, Overview, or Open Loops.
- **Selection**: The currently highlighted option or row on a screen; changes through keyboard input.
- **Navigation Stack**: The history of screens used to support Escape-based back navigation.
- **Person Form Draft**: In-progress Add Person values that must survive validation errors until saved or cancelled.
- **Existing NetOps Records**: People, relationships, interactions, open loops, suggestions, and evaluations already defined by the system and reused by the refactored interface.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can launch the terminal interface, open People, open a dossier, go back, open Add Person, save a person, and return to People without typing any navigation command.
- **SC-002**: 100% of required screens are reachable using only Up, Down, Enter, and Escape.
- **SC-003**: Selecting People from the Main Menu displays the People List in under 2 seconds for a local collection of 1,000 people.
- **SC-004**: A new person added through the terminal interface appears in the People List during the same session without restart.
- **SC-005**: Existing persisted people, interactions, open loops, suggestions, and evaluations remain readable after the refactor.
- **SC-006**: In usability validation, at least 90% of users can find "+ Add Person" from the Main Menu on their first attempt without being told a command name.

## Assumptions

- The terminal interface is the primary experience targeted by this refactor; direct CLI commands can continue to exist as secondary workflows.
- Existing domain models, storage schema, and service logic should be reused rather than redesigned.
- The Open Loops section may initially show a navigable list or placeholder screen if detailed open-loop editing is outside the immediate interaction refactor.
- Keyboard navigation targets standard terminal keys: Up, Down, Enter, and Escape.
- The cyberpunk aesthetic means terminal-native color, contrast, borders, selected-state styling, and status text; it does not require graphical assets or mouse interaction.
- Small terminal handling should prefer readable clipping or scrolling over trying to squeeze all content onto one screen.
- Add Person form drafts should live only for the current form session unless saved.
