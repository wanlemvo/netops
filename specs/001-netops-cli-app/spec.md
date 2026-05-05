# Feature Specification: NetOps CLI App

**Feature Branch**: `001-netops-cli-app`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Build a command-line application called NetOps that tracks people, logs interactions, and suggests next actions. The system should support two modes: Direct CLI commands (log, suggest, evaluate) and Interactive terminal interface (TUI) with a menu system. Core features: store people and relationships; log interactions with notes; track open loops and follow-ups; suggest next actions based on history; evaluate outcomes of actions. Interface should include overview dashboard, people directory, dossier view per person, interaction timeline, suggestions screen, evaluation screen. The system should be beginner-friendly, modular, and run locally using Python."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture People And Interactions (Priority: P1)

A beginner user can add people, describe relationships, and log interactions with notes so their relationship history is preserved in one local system.

**Why this priority**: NetOps is only useful if users can reliably record who they know and what has happened with each person.

**Independent Test**: Can be fully tested by adding a person, recording a relationship, logging an interaction with notes, and viewing the saved record in both command mode and the interactive menu.

**Acceptance Scenarios**:

1. **Given** a new local workspace, **When** the user adds a person with basic details and relationship context, **Then** the person appears in the people directory with the entered information.
2. **Given** an existing person, **When** the user logs an interaction with date, type, and notes, **Then** the interaction appears in that person's timeline and dossier.
3. **Given** a user enters incomplete required information, **When** they try to save a person or interaction, **Then** the system explains what is missing and allows them to correct it without losing entered context.

---

### User Story 2 - Review Relationship Context (Priority: P2)

A user can open an overview dashboard, browse the people directory, view a person's dossier, and inspect the interaction timeline to understand relationship status before deciding what to do next.

**Why this priority**: Users need fast recall of relationship context to make thoughtful follow-ups and avoid missed commitments.

**Independent Test**: Can be fully tested by loading sample people and interactions, then navigating from the dashboard to a directory entry, dossier, and timeline.

**Acceptance Scenarios**:

1. **Given** stored people, interactions, and open loops, **When** the user opens the overview dashboard, **Then** they see summary counts, upcoming follow-ups, overdue open loops, and recent activity.
2. **Given** multiple stored people, **When** the user opens the people directory, **Then** they can scan names, relationship context, last interaction, and open follow-up status.
3. **Given** a selected person, **When** the user opens the dossier view, **Then** they see key details, relationship notes, open loops, recent interactions, and evaluated outcomes for that person.

---

### User Story 3 - Get Suggested Next Actions (Priority: P3)

A user can ask NetOps what to do next and receive suggested actions based on interaction history, open loops, follow-ups, and relationship context.

**Why this priority**: The application's main value is converting stored relationship history into actionable next steps.

**Independent Test**: Can be fully tested by creating people with different histories and open loops, then confirming suggestions prioritize overdue, stale, and promised follow-ups.

**Acceptance Scenarios**:

1. **Given** a person has an overdue follow-up, **When** the user requests suggestions, **Then** that follow-up appears as a high-priority suggested next action with the reason shown.
2. **Given** a person has not been contacted recently, **When** the user requests suggestions, **Then** the system can suggest a check-in and explain the relevant history.
3. **Given** there are no urgent actions, **When** the user requests suggestions, **Then** the system communicates that clearly and may show lower-priority maintenance actions.

---

### User Story 4 - Evaluate Action Outcomes (Priority: P4)

A user can evaluate whether completed actions had positive, neutral, or negative outcomes so future suggestions reflect what worked.

**Why this priority**: Outcome evaluation closes the loop between recommendations and real-world results, improving the user's trust in future suggestions.

**Independent Test**: Can be fully tested by marking a suggested action as completed, recording its outcome, and verifying the evaluation appears in the person's dossier and affects future suggestion rationale.

**Acceptance Scenarios**:

1. **Given** a suggested or logged action has been completed, **When** the user evaluates the outcome, **Then** the system stores the result, notes, and date of evaluation.
2. **Given** evaluated outcomes exist for a person, **When** the user views the dossier, **Then** the system includes the outcome history alongside interactions and open loops.

### Edge Cases

- What happens when the user requests suggestions before any people or interactions exist?
- How does the system handle duplicate people with similar names?
- How does the system handle interactions logged with dates in the future or far in the past?
- What happens when an open loop is completed without a separate interaction note?
- How does the system recover if local data is missing, empty, or unreadable?
- How does the system keep command mode and interactive mode consistent when both operate on the same local records?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to create, view, update, and list people with basic identifying details and relationship context.
- **FR-002**: The system MUST allow users to record relationships between people or between the user and a person, including relationship type and notes.
- **FR-003**: Users MUST be able to log interactions for a person with a date, interaction type, freeform notes, and optional follow-up details.
- **FR-004**: The system MUST support open loops representing promised actions, unresolved topics, or follow-ups tied to a person and optionally tied to an interaction.
- **FR-005**: Users MUST be able to mark open loops as completed, deferred, or no longer relevant while preserving their history.
- **FR-006**: The system MUST provide direct command workflows for logging interactions, requesting suggestions, and evaluating outcomes.
- **FR-007**: The system MUST provide an interactive terminal menu that includes overview dashboard, people directory, dossier view, interaction timeline, suggestions screen, and evaluation screen.
- **FR-008**: The overview dashboard MUST show relationship activity summaries, recent interactions, open loops, due or overdue follow-ups, and available suggestions.
- **FR-009**: The people directory MUST show stored people in a scannable list with enough context to distinguish them, including last interaction and open follow-up status when available.
- **FR-010**: The dossier view MUST consolidate a person's details, relationship context, open loops, timeline highlights, suggestions, and outcome evaluations.
- **FR-011**: The interaction timeline MUST present interactions in chronological order and allow users to filter or focus by person.
- **FR-012**: The suggestions screen and suggest command MUST generate next actions using stored history, open loops, due dates, stale relationships, and prior outcomes.
- **FR-013**: Each suggested action MUST include a clear reason so the user understands why it was recommended.
- **FR-014**: Users MUST be able to evaluate an action outcome with status, notes, and optional relationship impact.
- **FR-015**: The system MUST store all user-entered records locally and make them available across application sessions.
- **FR-016**: The system MUST guide beginner users with clear labels, confirmation messages, recoverable prompts, and helpful validation errors.
- **FR-017**: The system MUST avoid losing entered information when validation fails during command or interactive workflows.
- **FR-018**: The system MUST provide a way to inspect empty-state guidance when no people, interactions, open loops, suggestions, or evaluations exist.
- **FR-019**: The system MUST keep behavior consistent between direct commands and equivalent interactive menu actions.
- **FR-020**: The system MUST preserve historical interactions, open-loop changes, suggestions acted upon, and evaluations for later review.

### Key Entities

- **Person**: A human contact tracked by the user; includes name, optional contact details, tags or categories, relationship context, notes, and timestamps for creation and updates.
- **Relationship**: A described connection involving a person; includes relationship type, related person when applicable, strength or context notes, and history-relevant details.
- **Interaction**: A recorded event with a person; includes date, interaction type, notes, related open loops, and any follow-up created from it.
- **Open Loop**: An unresolved commitment, topic, or follow-up; includes owner person, description, status, due date when available, source interaction when available, and resolution history.
- **Suggested Action**: A recommended next step; includes target person, action description, priority, reason, related history, and status if accepted, ignored, or completed.
- **Evaluation**: A review of an action outcome; includes evaluated action or interaction, outcome rating, notes, date, and observed relationship impact.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can add a person and log their first interaction in under 3 minutes without reading external documentation.
- **SC-002**: A user can reach any required screen in the interactive menu within 3 menu selections from the main menu.
- **SC-003**: Users can request suggested next actions and see prioritized results with reasons in under 5 seconds for a local collection of 1,000 people and 10,000 interactions.
- **SC-004**: At least 90% of primary workflows tested by users are completable in both direct command mode and interactive mode.
- **SC-005**: 100% of saved people, interactions, open loops, suggestions acted upon, and evaluations remain available after closing and reopening the application.
- **SC-006**: In usability testing, at least 85% of beginner users can correctly identify their next follow-up from the dashboard or suggestions screen on the first attempt.

## Assumptions

- The application is intended for a single local user managing a personal or professional relationship network.
- Multi-user collaboration, synchronization across devices, and hosted online accounts are out of scope for the initial feature.
- The user controls their local data and is responsible for appropriate handling of sensitive personal notes.
- Suggestions are explainable recommendations based on recorded history and rule-like prioritization, not guaranteed predictions of relationship outcomes.
- Contact communication such as sending emails, messages, or calendar invitations is out of scope unless added by a later feature.
- Beginner-friendly means clear terminology, guided prompts, safe validation, and useful empty states rather than requiring prior command-line expertise.
