# NetworkOps V1 Architecture

## Purpose

This document describes the technical design needed to support the NetworkOps V1 Person Intelligence Record system described in `specs/004-person-intelligence-record/spec.md`.

NetworkOps V1 should remain a local-first CLI application while moving away from a flat contact tracker. The architecture should preserve structured person data, long-form relationship context, interaction history, standalone notes, signals, opportunities, and future graph-style relationships without implementing future AI, semantic search, graph visualization, or automation.

## Core Entities

### Person

The central intelligence record for an individual. A person stores durable identity and relationship context, including name, alias, role, organization, location, birthday, profile photo reference, relationship type, relationship strength, origin story, importance reason, dossier, interests, communication style, preferences, signals summary, current goals, potential value, mutual connections, first met, last contact, next action, follow-up date, and timestamps.

### Contact Method

A structured way to reach or identify a person. Contact methods should support email, phone, LinkedIn, GitHub, and other social or external identifiers. Keeping these separate from freeform notes makes them reusable for future search, export, validation, and automation.

### Interaction Log

A dated record of an event, conversation, meeting, call, introduction, or meaningful relationship touchpoint. V1 should support one primary linked person, while leaving room for future multiple participants. Interaction logs capture summary, takeaways, action items, sentiment, follow-up required status, interaction date, and timestamps.

### Note

A user-authored note that can exist independently from any one person. Notes should support title, content, tags, and creation metadata. Future versions may link notes to multiple people, opportunities, signals, or interactions, but V1 should not require a person association.

### Signal

An observed relationship insight, preference, value, pattern, or inference. Signals should include signal text, confidence, source context, optional person association, and timestamps. Signals are separate from the person record so multiple signals can accumulate over time instead of being flattened into one field.

### Opportunity

A possible relationship action or opening, such as a mock interview, introduction, mentorship path, referral, or follow-up conversation. Opportunities should include title, linked person or owner, status, description, follow-up date, and timestamps.

### Relationship Link

A general-purpose link between records. Relationship links prepare the system for future graph-style connections by allowing one entity to reference another without hardcoding every possible relationship into the person table. V1 can keep this modest and use it only where useful, but the shape should support future cross-linking and backlinks.

## Entity Relationships

```text
Person
    -> many Contact Methods
    -> many Interaction Logs
    -> many Signals
    -> many Opportunities
    -> many Relationship Links

Note
    -> may exist independently
    -> may eventually link to multiple People
    -> may eventually link to Logs, Signals, or Opportunities

Interaction Log
    -> belongs to one primary Person in V1
    -> may eventually involve multiple People

Relationship Link
    -> connects one entity to another entity
    -> prepares for future graph-style relationships and backlinks
```

For V1, direct foreign keys should handle the most important relationships: people to contact methods, interaction logs, signals, and opportunities. Relationship links should exist as a flexible extension point for future cross-linking, backlinks, and graph-like navigation.

## Storage Strategy

NetworkOps V1 should use a local-first storage model. The app should work without a server, account, or cloud dependency. Since the current product is a CLI app with structured records, SQLite is the preferred storage layer.

SQLite is a good fit because it is portable, durable, file-based, transactional, and well suited for relational data such as people, contact methods, logs, notes, signals, opportunities, tags, and links. It also keeps the app easy to move as a folder because the database can live inside the app's `data/` directory.

Recommended local data layout:

```text
data/
    netops.db
    assets/
        profile_photos/
```

The database should store structured records and references to local files. Profile photos should be stored as local files, with only a relative path or asset reference stored in the database. The database should not store profile photos as blobs for V1.

## Table / Data Model Draft

This draft is intentionally implementation-ready but not final code. It identifies the tables and fields the V1 implementation should plan around.

### people

Stores the central person intelligence record.

```text
id
name
alias
role
organization
location
birthday
profile_photo_path
relationship_type
relationship_strength
origin_story
importance_reason
dossier
interests
communication_style
preferences
signals_summary
current_goals
potential_value
mutual_connections
first_met
last_contact
next_action
follow_up_date
created_at
updated_at
archived_at
```

### contact_methods

Stores structured contact data for people.

```text
id
person_id
type
label
value
is_primary
created_at
updated_at
```

Example `type` values: `email`, `phone`, `linkedin`, `github`, `other_social`.

### interaction_logs

Stores dated relationship events.

```text
id
person_id
interaction_date
summary
takeaways
action_items
sentiment
follow_up_required
created_at
updated_at
```

V1 uses `person_id` for one primary person. Future multiple participants can be supported with a join table such as `interaction_participants` without replacing this table.

### notes

Stores user-authored notes that may exist independently.

```text
id
title
content
created_at
updated_at
archived_at
```

Notes should not require `person_id`. Future links to people or other records should be handled through relationship links or join tables.

### signals

Stores relationship intelligence observations.

```text
id
person_id
signal_text
confidence
source_type
source_id
created_at
updated_at
```

`person_id` should be optional if the signal is known before it is attached to a person. `source_type` and `source_id` can reference where the signal came from, such as an interaction log or note.

### opportunities

Stores possible relationship actions or openings.

```text
id
person_id
title
status
description
follow_up_date
created_at
updated_at
closed_at
```

Example `status` values: `open`, `pending`, `complete`, `closed`.

### relationship_links

Stores flexible links between records.

```text
id
source_entity_type
source_entity_id
target_entity_type
target_entity_id
relationship_type
description
created_at
updated_at
```

This table prepares for backlinks and graph-style relationships. For example, it could later link a note to multiple people, a signal to an interaction, or an opportunity to a note.

### tags

Tags may be useful if tags need consistent reuse, filtering, or cross-entity tagging.

```text
id
name
created_at
```

### taggings

Allows tags to attach to more than one entity type.

```text
id
tag_id
entity_type
entity_id
created_at
```

If V1 only needs simple person tags, tags could remain a text field initially. If filtering and reuse matter in V1, use `tags` and `taggings`.

## Long-Form Text Strategy

Long-form relationship intelligence must be stored without truncation and edited without being constrained by the visible terminal width or height.

Long-form fields include:

- `dossier`
- `origin_story`
- `importance_reason`
- `notes.content`
- `interaction_logs.summary`
- `interaction_logs.takeaways`
- `interaction_logs.action_items`
- `signals.signal_text`
- `opportunities.description`
- other person context fields such as interests, communication style, preferences, current goals, potential value, and mutual connections

Storage guidance:

- Store long-form fields as SQLite `TEXT`.
- Do not apply artificial length limits unless required by a specific product rule.
- Preserve newline characters exactly as entered.
- Preserve pasted multiline content.
- Normalize line endings only if needed for consistent display, and do not remove user formatting.
- Avoid storing long-form content in fixed-width display buffers.

CLI behavior guidance:

- Short fields can use single-line prompts.
- Long-form fields need a multiline entry strategy.
- Viewing long-form text should wrap or scroll instead of truncating.
- Editing long-form text should not depend on whether the whole value fits in the visible window.
- Save behavior should operate on the complete field value, not only the visible slice of text.

## Migration Strategy

Existing contact records must remain accessible after the schema change. The migration should not require manual cleanup.

Recommended migration approach:

1. Add new tables and columns without deleting existing data.
2. Map existing person/contact fields into the new `people` shape.
3. Preserve unknown or older fields in the closest compatible field rather than dropping them.
4. Convert existing phone, email, social, or contact-like values into `contact_methods` where possible.
5. Leave missing optional V1 fields blank or unset.
6. Ensure old person records can still be listed, opened, edited, and saved.
7. Make migrations repeatable and versioned so a partially migrated database can be detected safely.
8. Keep a backup-friendly posture: because the app is local-first, the database file should be easy to copy before migration.

The migration should prioritize data preservation over perfect normalization. If a legacy field cannot be confidently mapped, it should remain available in a notes or legacy context field until a later cleanup path exists.

## Profile Photo Strategy

Profile photos should be stored as local assets, not database blobs.

Recommended behavior:

- Copy or import selected photos into `data/assets/profile_photos/`.
- Store a relative path or asset reference in `people.profile_photo_path`.
- Prefer stable generated filenames to avoid collisions.
- Keep the database portable by avoiding absolute machine-specific paths when possible.
- Display the photo when the current interface supports image display.
- In CLI-only contexts that cannot render images, show the photo filename/path and whether the file exists.
- If the file is missing, show a clear missing-photo state and keep the stored reference for repair.
- If the file type is unsupported, keep the reference but show a clear unsupported-photo state.
- Do not block opening or editing a person record because the photo is missing or unsupported.

Supported formats should be intentionally narrow at first, such as common local image formats. Broader media handling can be added later.

## Architecture Decisions Needed

The following ADRs should be created and maintained alongside the implementation:

- `0001-use-sqlite-local-first.md`: Decide that NetworkOps V1 uses SQLite for local-first structured storage.
- `0002-separate-person-records-from-event-records.md`: Decide that people are separate from interaction logs, notes, signals, and opportunities.
- `0003-store-profile-photos-as-local-assets.md`: Decide that profile photos are stored as local files with database references.
- `0004-support-long-form-multiline-text.md`: Decide that long-form fields must preserve multiline content and avoid visible-window truncation.
- `0005-design-for-future-relationship-graph.md`: Decide that relationship links should prepare the system for future graph-style relationships and backlinks.

## Non-Goals

NetworkOps V1 architecture should not include:

- AI implementation
- Semantic search
- Graph visualization
- Automation
- Cloud sync
- Multi-user collaboration
- External social network integrations
- Scope beyond `specs/004-person-intelligence-record/spec.md`

The architecture should make future expansion possible, but the V1 design should stay focused on local-first person intelligence records and the supporting entities named in the feature spec.
