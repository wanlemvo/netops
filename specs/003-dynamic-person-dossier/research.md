> Historical design record; not current product instructions. See the [current README](../../README.md).

# Research: Dynamic Person Dossier

## Decision: Use additive SQLite migrations for dossier fields

The existing `people` table will gain optional scalar profile columns: `alias`, `role`, `location`, `relationship_type`, `relationship_strength`, `birthday`, `communication_style`, `preferences_notes`, `interests`, and `signals`. List fields will be stored as JSON text, matching the current `tags` storage pattern.

**Rationale**: This preserves existing people IDs and repository patterns while keeping profile reads simple for the local TUI. JSON text is already used for simple list data in the project, so interests and signals can follow the same approach without introducing more joins for low-cardinality local data.

**Alternatives considered**: A separate table per profile section would be more normalized but adds repository complexity without a current multi-user or reporting requirement. A single JSON profile blob would be compact but makes field-level validation, migrations, and direct CLI compatibility harder.

## Decision: Store raw notes in a separate append-only table

Add a `person_notes` table with `id`, `person_id`, `note`, `created_at`, and optional `source`. The dossier interface appends rows and never overwrites or deletes them.

**Rationale**: Append-only behavior is a core requirement. A separate table makes preservation testable and avoids replacing a large freeform text field by accident.

**Alternatives considered**: Reusing `relationship_notes` would risk destructive replacement. Reusing `interactions` with type `note` would blend raw dossier notes with interaction history, making "raw notes separately" less clear.

## Decision: Derive last contact from interactions

The dossier Interaction section will calculate `last_contact` from the newest existing interaction for the person, using `occurred_on` and the repository's existing date ordering.

**Rationale**: Last contact is derived state and should stay consistent with actual interaction history. It avoids a redundant column that could drift.

**Alternatives considered**: Persisting `last_contact` on `people` would be faster but introduces synchronization risk. The local dataset target makes a derived query acceptable.

## Decision: Reuse open loops as commitments

The Opportunity section will display person-tied open loops as commitments and keep existing open-loop behavior unchanged.

**Rationale**: The current app already models follow-ups with person IDs, status, due dates, and priorities. Reusing it preserves behavior and avoids a parallel task model.

**Alternatives considered**: A new `commitments` table would duplicate concepts and require extra sync logic with suggestions/evaluations.

## Decision: Implement field-by-field editing through service allowlists

`PeopleService` will expose profile field metadata and update one allowed field at a time. Validation will normalize relationship strength and comma-separated list fields before persistence.

**Rationale**: A service-level allowlist keeps the TUI simple and prevents arbitrary attribute writes. It also gives direct CLI commands a stable reuse point if future commands expose dossier editing.

**Alternatives considered**: Letting the TUI mutate `Person` directly would scatter validation. A generic repository update would be flexible but easier to misuse.

## Decision: Keep dossier navigation modular and screen-oriented

The dossier feature will extend the keyboard TUI with dossier-specific screen/view-model helpers rather than routing add, view, edit, or append-note actions through direct CLI command callbacks. Shared TUI modules continue to own application assembly, navigation state, reusable screen primitives, and theme tokens; dossier-specific section building and actions live in a focused dossier module.

**Rationale**: The requested interface is closer to a structured case-file browser than a command utility. A screen-oriented architecture keeps the People index, Dossier View, Edit Profile, and Append Raw Note flows predictable and testable while avoiding a large mixed-purpose `screens.py`.

**Alternatives considered**: Reusing Typer commands internally would keep implementation surface smaller but would preserve the command-heavy mental model the feature is explicitly replacing. Putting all rendering and dossier behavior in one TUI file would be faster initially but harder to maintain as sections and editable fields grow.

## Decision: Group people in the service or screen model, not storage

The People List will sort by display name and add non-activating first-letter header rows. Names beginning with numbers, symbols, or empty trimmed values will group under `#`.

**Rationale**: Grouping is display behavior. Keeping it out of persistence avoids schema churn and makes keyboard tests straightforward.

**Alternatives considered**: Persisting sort keys or groups is unnecessary for the current 1,000-person target and would require update logic whenever names change.

## Decision: Use wrapped/clipped text in existing TUI screen rendering

Long notes and long lists will be rendered as wrapped rows where supported by the current screen renderer, with clipping/scroll indicators consistent with the 002 navigation refactor.

**Rationale**: The current TUI already has visible-row and clipped-row behavior. Extending that pattern avoids a new terminal framework and keeps the UI keyboard-driven.

**Alternatives considered**: Full rich text panes or nested scroll areas would add complexity and risk recreating GUI-style behavior.
