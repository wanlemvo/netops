# Prompt Log and Workflow Timeline

This log summarizes the major prompts, decisions, and workflow checkpoints that led to the final NetOps CLI/TUI implementation. It is curated rather than copied from raw chat history so it can show the development process clearly without exposing unnecessary local or conversational detail.

## 1. Initial Direction: Build a Local NetOps CLI

**Goal**  
Start from the idea of a local-first relationship tracking tool that could store people, interactions, open loops, and follow-up suggestions.

**Representative Prompt**  
"Build a NetOps CLI app for tracking people, interactions, follow-ups, suggestions, and evaluations."

**What Happened**  
The first phase established the baseline application shape: Python package, Typer CLI commands, SQLite persistence, services, domain models, and tests. This gave the project a working foundation before the more advanced TUI work started.

**Key Decisions**
- Use a local SQLite database instead of an external service.
- Keep domain models and service logic separate from CLI presentation.
- Make follow-up suggestions rule-based rather than analytics-heavy.

## 2. Interaction Problem Identified: The UI Felt Too Command-Heavy

**Goal**  
Refactor the interface so users could navigate with the keyboard instead of typing command-style paths for every action.

**Representative Prompt**  
"Feature: Navigation System Refactor (Keyboard-Driven Terminal UI). Replace the current command-based and incorrect UI with arrow-key navigation, Enter to select, and Escape to go back."

**What Happened**  
This became the `002-keyboard-tui-nav` feature. SpecKit was used to define the behavior before implementation: Main Menu, People List, Dossier View, Add Person Form, Overview, and Open Loops.

**Key Decisions**
- Use `prompt_toolkit` for keyboard-driven terminal behavior.
- Keep existing direct CLI commands, but stop using command parsing as the internal navigation model.
- Split TUI concerns into `app.py`, `state.py`, `screens.py`, and `theme.py`.

## 3. Design Direction Shift: Make the Interface Feel Like a Dossier System

**Goal**  
Move beyond a generic terminal utility and make the interface feel like a structured dossier browser.

**Representative Prompt**  
"Prioritize maintainable file structure and modular CLI navigation. The interface should resemble a structured dossier system rather than a traditional command-heavy terminal utility."

**What Happened**  
This became the planning direction for `003-dynamic-person-dossier`. The project shifted from simply listing people to treating each person as an expandable profile with structured sections.

**Key Decisions**
- Add a dossier-specific TUI module instead of letting `screens.py` become too large.
- Structure a person profile into Identity, Relationship, Personal Intelligence, Interaction, Opportunity, and Raw Notes.
- Keep advanced analytics and graph/network logic out of the first implementation slice.

## 4. SpecKit Planning Phase

**Goal**  
Use SpecKit to produce a concrete implementation plan from the dossier concept.

**Representative Prompt**  
"Run the SpecKit planning workflow for the dynamic person dossier feature."

**What Happened**  
The planning phase produced the main design artifacts:

- `specs/003-dynamic-person-dossier/spec.md`
- `specs/003-dynamic-person-dossier/plan.md`
- `specs/003-dynamic-person-dossier/research.md`
- `specs/003-dynamic-person-dossier/data-model.md`
- `specs/003-dynamic-person-dossier/contracts/`
- `specs/003-dynamic-person-dossier/quickstart.md`

**Key Decisions**
- Use additive SQLite migrations for new dossier fields.
- Store raw notes in an append-only `person_notes` table.
- Derive last contact from interactions instead of storing duplicate state.
- Reuse open loops as commitments.
- Use service-level editable-field allowlists for safer profile updates.

## 5. Task Generation Phase

**Goal**  
Turn the plan into ordered, executable tasks.

**Representative Prompt**  
"Focus implementation tasks on core workflows first: person creation, person overview, interaction logging, follow-up suggestions. Delay advanced analytics and graph/network logic."

**What Happened**  
SpecKit generated `specs/003-dynamic-person-dossier/tasks.md`, organized by phases and user stories. The task list intentionally prioritized the core workflow spine first.

**Key Decisions**
- Build in this order:
  1. Person creation
  2. Person overview
  3. Interaction logging
  4. Follow-up suggestions
- Delay profile editing, raw notes, and grouped browsing until after the core spine was stable.
- Keep graph/network logic explicitly deferred.

## 6. Implementation Phase: Data Foundation

**Goal**  
Implement the storage and domain changes needed for structured dossiers.

**Representative Prompt**  
"Execute the implementation plan by processing and executing all tasks defined in tasks.md."

**What Happened**  
The implementation added dossier fields to the `Person` model and introduced append-only raw notes.

**Key Changes**
- Extended `src/netops/domain/models.py` with dossier fields.
- Added validation helpers in `src/netops/domain/validation.py`.
- Added SQLite migration v2 in `src/netops/storage/migrations.py`.
- Updated repository mapping in `src/netops/storage/repositories.py`.

**Decision Checkpoint**
The migration was kept additive so existing people remained readable after the upgrade.

## 7. Implementation Phase: Dossier Services

**Goal**  
Make dossier behavior available through services instead of making the TUI mutate records directly.

**Representative Prompt**  
"Keep implementation modular and avoid overengineering; use services for validation and persistence."

**What Happened**  
The people service became the main interface for dossier operations.

**Key Changes**
- Minimal person creation still requires only a name.
- Dossier reads include profile fields, interactions, suggestions, evaluations, raw notes, and last contact.
- Profile editing uses an allowlist.
- Raw note append behavior preserves previous notes.

**Decision Checkpoint**
Validation was placed in the service/domain layer so future CLI or TUI features can reuse the same rules.

## 8. Implementation Phase: TUI Dossier Workflow

**Goal**  
Make the terminal interface support the dossier workflow directly.

**Representative Prompt**  
"The interface should resemble a structured dossier system rather than a traditional command-heavy terminal utility."

**What Happened**  
The TUI was extended with dossier-specific screens and state transitions.

**Key Changes**
- Added `src/netops/tui/dossier.py`.
- Updated `src/netops/tui/state.py` with drafts for interaction logging, edit-field, and raw-note forms.
- Updated `src/netops/tui/screens.py` with structured dossier rendering and form screens.
- Added grouped People List headers while keeping headers non-activating.

**Decision Checkpoint**
The TUI kept the keyboard model: Up/Down to move, Enter to activate, Escape to return.

## 9. Testing and Debugging Phase

**Goal**  
Validate the implementation against existing behavior and new dossier requirements.

**Representative Prompt**  
"Run tests, inspect failures, and fix the implementation without breaking existing direct CLI workflows."

**What Happened**  
Tests exposed issues during implementation, including migration syntax, old tests expecting evaluation counts, grouped header selection behavior, and deterministic raw-note ordering.

**Key Fixes**
- Fixed migration list syntax.
- Preserved evaluation visibility in dossier output.
- Adjusted selection so disabled group headers are visible but not accidentally selected during normal movement.
- Ordered raw notes deterministically by insertion order.

**Validation Result**
Final test run:

```text
python -m pytest
61 passed
```

## 10. Submission Artifact Phase

**Goal**  
Check the project against the midterm requirements and add missing non-code artifacts.

**Representative Prompt**  
"Does this satisfy my assignment requirements?"

**What Happened**  
The repository already contained strong SpecKit artifacts and implementation evidence, but the midterm required additional reflection artifacts.

**Artifacts Added**
- `model_selection_justification.md`
- `responsible_ai_analysis.md`
- `prompt_log.md`

**Key Decisions**
- Use a curated timeline instead of dumping raw chat history.
- Keep model comparison realistic and tradeoff-based.
- Ground responsible AI analysis in summarization, source bias, privacy/logging, hallucination, and overreliance risks.

## 11. Workflow Reflection

**What Worked**
- SpecKit made the workflow traceable from requirements to tasks to code.
- Keeping a task list helped avoid drifting into advanced graph/network features too early.
- Codex was useful for implementation because it could edit files, run tests, and update tasks as work completed.

**What Changed Along the Way**
- The project started as a command-oriented CLI.
- It evolved into a keyboard-driven terminal system.
- It then became a structured dossier workflow with modular TUI navigation.

**What Was Intentionally Deferred**
- Advanced analytics.
- Network graph visualization.
- Relationship graph traversal.
- Bulk intelligence scoring.

**Final State**
The final product supports the core workflows required for the practical assessment: person creation, person overview, interaction logging, follow-up suggestions, profile editing, raw notes, tests, and supporting SpecKit artifacts.
