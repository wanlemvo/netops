> Historical design record; not current product instructions. See the [current README](../README.md).

# NetworkOps V1 Data Model

## Purpose

This document defines the NetworkOps V1 entities before schema implementation. It is based on `specs/004-person-intelligence-record/spec.md`, `docs/architecture/networkops_v1_architecture.md`, and ADRs 0001-0008.

NetworkOps V1 is a local-first Personal Relationship Intelligence System. People are the primary entity. All other entities exist to preserve context around people: conversations, observations, opportunities, notes, contact methods, and relationships.

This document does not define migrations or implementation code.

## Scope

Included in V1 data modeling:

- Person
- Contact Method
- Interaction Log
- Note
- Signal
- Opportunity
- Relationship Link
- Tags and taggings, if structured tagging is needed

Outside V1 scope:

- AI
- Semantic search
- Graph visualization
- Automation
- Recommendation systems
- Voice interfaces

## Identity Strategy

Every primary record should use a stable UUID as its true identity. Human-readable names, titles, labels, emails, phone numbers, and social accounts are attributes, not identity.

Person records must not rely on `name` uniqueness. Duplicate-looking records should be allowed, with duplicate detection warnings handled separately from record creation.

## Entity Overview

```text
Person
    -> Contact Method
    -> Interaction Log
    -> Signal
    -> Opportunity
    -> Relationship Link

Note
    -> can exist independently
    -> can link to people or other records through Relationship Link

Relationship Link
    -> connects people, notes, interactions, signals, opportunities, and future records
```

## Person

The central relationship intelligence record for an individual.

### Fields

```text
person_id
name
alias
role
organization
location
birthday
profile_photo_path
relationship_type
relationship_status
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

### Field Notes

- `person_id` is the stable UUID for the record.
- `name` is required.
- All other fields are optional.
- `profile_photo_path` stores a local asset reference, not image binary data.
- `relationship_type` should use a controlled vocabulary where possible.
- `relationship_status` should use a controlled vocabulary such as `active`, `dormant`, or `archived`.
- Long-form fields include `origin_story`, `importance_reason`, `dossier`, `interests`, `communication_style`, `preferences`, `signals_summary`, `current_goals`, `potential_value`, and `mutual_connections`.

## Contact Method

A structured way to reach or identify a person.

### Fields

```text
contact_method_id
person_id
type
label
value
normalized_value
is_primary
created_at
updated_at
archived_at
```

### Field Notes

- `contact_method_id` is the stable UUID for the contact method.
- `person_id` links the contact method to a person.
- `type` should use a controlled vocabulary such as `email`, `phone`, `linkedin`, `github`, or `other_social`.
- `label` can distinguish values such as `work`, `personal`, `primary`, or `old`.
- `value` stores the user-facing value.
- `normalized_value` stores a comparison-friendly value for duplicate detection and lookup when useful.
- `is_primary` identifies the preferred value for a type.

## Interaction Log

A dated relationship event such as a meeting, call, introduction, conversation, or meaningful touchpoint.

### Fields

```text
interaction_log_id
person_id
interaction_date
summary
takeaways
action_items
sentiment
follow_up_required
follow_up_date
created_at
updated_at
archived_at
```

### Field Notes

- `interaction_log_id` is the stable UUID for the interaction log.
- `person_id` is the primary linked person for V1.
- Future multiple participants should be supported through explicit relationship links or a participant join table.
- `summary`, `takeaways`, and `action_items` are long-form multiline text fields.
- `sentiment` should use a controlled vocabulary if used for filtering.
- `follow_up_required` is a structured boolean value.

## Note

A user-authored knowledge record. A note may exist independently and does not require a person.

### Fields

```text
note_id
title
content
created_at
updated_at
archived_at
```

### Field Notes

- `note_id` is the stable UUID for the note.
- `title` is a short user-facing label.
- `content` is a long-form multiline text field.
- Notes can later link to multiple people, interactions, signals, or opportunities through relationship links.
- Notes should not be forced into person records.

## Signal

An observed relationship insight, preference, value, behavior, pattern, or piece of intelligence.

### Fields

```text
signal_id
person_id
signal_text
confidence
source_entity_type
source_entity_id
created_at
updated_at
archived_at
```

### Field Notes

- `signal_id` is the stable UUID for the signal.
- `person_id` is optional if the signal has not yet been attached to a person.
- `signal_text` is a long-form text field.
- `confidence` should use a controlled vocabulary such as `low`, `medium`, or `high`.
- `source_entity_type` and `source_entity_id` identify where the signal came from when known.
- Sources may include an interaction log, note, opportunity, or manual entry.

## Opportunity

A possible relationship action or opening connected to a person or relationship context.

### Fields

```text
opportunity_id
person_id
title
status
owner_person_id
description
follow_up_date
created_at
updated_at
closed_at
archived_at
```

### Field Notes

- `opportunity_id` is the stable UUID for the opportunity.
- `person_id` links the opportunity to the primary related person when known.
- `owner_person_id` identifies the person who owns, sponsors, or is most responsible for the opportunity when different from `person_id`.
- `status` should use a controlled vocabulary such as `open`, `pending`, `complete`, or `closed`.
- `description` is a long-form multiline text field.
- `follow_up_date` supports relationship operations and open-loop review.

## Relationship Link

A flexible explicit link between two records.

### Fields

```text
relationship_link_id
source_entity_type
source_entity_id
target_entity_type
target_entity_id
relationship_type
description
created_at
updated_at
archived_at
```

### Field Notes

- `relationship_link_id` is the stable UUID for the relationship link.
- `source_entity_type` and `target_entity_type` identify the linked entity types.
- `source_entity_id` and `target_entity_id` store the linked record IDs.
- `relationship_type` describes the link, such as `mentions`, `related_to`, `participant`, `source_of`, `introduced_by`, `supports`, or `owns`.
- `description` can preserve human context for why the link exists.

### Initial Relationship Types

V1 should prepare for these explicit links:

- person <-> note
- person <-> interaction
- person <-> signal
- person <-> opportunity
- person <-> person

## Tags

Tags support flexible classification and discovery. Structured fields should be preferred when values come from a controlled list.

### tags

```text
tag_id
name
normalized_name
created_at
updated_at
archived_at
```

### taggings

```text
tagging_id
tag_id
entity_type
entity_id
created_at
```

### Field Notes

- Tags are optional for V1 if simple person-level tags are enough.
- Use controlled fields for operational concepts such as relationship type, relationship status, opportunity status, confidence, sentiment, and contact method type.
- Use tags for flexible discovery labels that do not need workflow meaning.

## Long-Form Text Fields

Long-form fields must support pasted multiline content without truncation.

Long-form fields include:

- `people.origin_story`
- `people.importance_reason`
- `people.dossier`
- `people.interests`
- `people.communication_style`
- `people.preferences`
- `people.signals_summary`
- `people.current_goals`
- `people.potential_value`
- `people.mutual_connections`
- `interaction_logs.summary`
- `interaction_logs.takeaways`
- `interaction_logs.action_items`
- `notes.content`
- `signals.signal_text`
- `opportunities.description`
- `relationship_links.description`

Storage expectations:

- Store long-form values as text.
- Preserve line breaks.
- Preserve pasted paragraphs and bullets.
- Do not truncate content based on terminal width or height.
- Do not treat visible text as the complete stored value.

## Duplicate Detection Inputs

Potential duplicate person warnings should eventually compare:

- Name similarity
- Email contact methods
- Phone contact methods
- LinkedIn contact methods
- GitHub contact methods
- Other social accounts

Duplicate detection should warn the user without preventing record creation.

## Migration Expectations

Existing records should remain accessible after schema implementation.

Migration should:

- Preserve existing people.
- Map existing known fields into the V1 person fields.
- Convert contact-like values into contact methods when possible.
- Leave unknown optional fields blank.
- Preserve long-form legacy notes or context in the closest compatible field.
- Avoid manual cleanup requirements.
- Avoid deleting legacy data during the initial migration.

## Non-Goals

The V1 data model does not include:

- AI
- Semantic search
- Graph visualization
- Automation
- Recommendation systems
- Voice interfaces
- Cloud sync
- Multi-user collaboration
