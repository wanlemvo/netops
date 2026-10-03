> Historical design record; not current product instructions. See the [current README](../../README.md).

# Research: NetworkOps Person Intelligence Record

## Decision: Use SQLite for local-first structured storage

**Rationale**: NetworkOps is a portable single-user CLI/TUI application. SQLite supports durable local data, transactions, indexes, migrations, and easy folder-based portability without a server or cloud account.

**Alternatives considered**:

- JSON files: simpler initially, but weak for relational queries, migrations, indexing, and multi-entity integrity.
- Graph database: attractive for relationship traversal, but excessive for V1 and conflicts with the local CLI simplicity goal.
- Hosted database: out of scope because V1 is local-first.

## Decision: Use UUID text identifiers for primary entities

**Rationale**: Names are not unique. UUIDs preserve stable identity for people, interactions, signals, opportunities, and links while allowing duplicate-looking names and imperfect real-world data.

**Alternatives considered**:

- Name-based identity: rejected because `Isaac`, `Rei`, `Dr. Olav`, and `Dr Olav` may be duplicate-looking or distinct records.
- Integer-only identity: workable locally, but UUIDs better support future import/export, merge, and graph-like linking.

## Decision: People are the primary entity

**Rationale**: NetworkOps is about preserving relationship intelligence around people. Contact methods, interactions, signals, opportunities, and links exist to provide context around people.

**Alternatives considered**:

- Note-first model: rejected because NetOps V1 is not a note-taking app or personal wiki.
- Opportunity-first model: rejected because opportunities are contextual outcomes, not the core identity layer.

## Decision: Exclude standalone notes from NetOps V1

**Rationale**: The approved schema removes standalone notes from scope. Note-like content should be preserved during migration, but V1 should not create a general notes entity. This keeps NetOps focused on relationship intelligence rather than becoming a knowledge management system.

**Alternatives considered**:

- Keep `notes` as a V1 entity: rejected because it expands NetOps toward a wiki/knowledge-base shape and conflicts with the latest scope direction.
- Delete legacy notes: rejected because migration must preserve existing local data.

## Decision: Keep signals as the relationship-intelligence entity name

**Rationale**: The final schema cleanup keeps `signals`, not observations. Signals capture learned relationship intelligence such as values, preferences, interests, hiring context, or response patterns.

**Alternatives considered**:

- Rename to observations: rejected by latest product direction.

## Decision: Support multi-person interactions and opportunities through join tables

**Rationale**: Real meetings and opportunities often involve more than one person. Join tables keep interactions and opportunities independent while preserving person context and role metadata.

**Alternatives considered**:

- Store one `person_id` directly on interactions/opportunities only: rejected because it cannot represent multi-person reality.
- Store comma-separated names: rejected because it breaks UUID identity and relationship integrity.

## Decision: Use relationship links for person-to-person relationship intelligence

**Rationale**: `relationship_links` provide the single source of truth for person-to-person connections such as mentors, knows, works_with, introduced_by, and other extensible relationship types.

**Alternatives considered**:

- Store mutual connections as long text on people: rejected because it duplicates relationship information and conflicts with link-based architecture.
- Hardcode relationship types: rejected because personal relationship data needs extensibility.

## Decision: Store profile photos as local assets

**Rationale**: Local files keep the database small and portable. Storing relative paths supports moving the portable folder across machines.

**Alternatives considered**:

- Database blobs: rejected for V1 because they make the database heavier and complicate simple asset handling.
- Remote URLs: rejected because V1 is local-first and should not depend on external availability.

## Decision: Store long-form fields as unrestricted text

**Rationale**: Relationship intelligence depends on pasted paragraphs, bullets, summaries, takeaways, and multiline context. The app must not truncate values based on terminal size.

**Alternatives considered**:

- Fixed-length strings: rejected because they recreate the current text-entry limitation.
- Rich text: rejected because V1 only needs preserved multiline plain text.

## Decision: Controlled values are validated by application rules in V1

**Rationale**: Fields such as relationship type, relationship status, interaction type, sentiment, signal confidence, and opportunity status benefit from consistency, but V1 should remain flexible while product vocabulary stabilizes.

**Alternatives considered**:

- Strict lookup tables for all controlled values: deferred until vocabulary settles.
- Freeform tags for everything: rejected due to tag sprawl and weak filtering.
