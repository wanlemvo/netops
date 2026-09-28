# NetworkOps V1 Schema Design

## Purpose

This document defines the final NetworkOps V1 schema design to be implemented in SQLite later. It is based on:

- `specs/004-person-intelligence-record/spec.md`
- `docs/architecture/networkops_v1_architecture.md`
- `docs/adr/`
- `docs/data_model_v1.md`
- `docs/project_audit.md`

This document is schema design only. It does not define SQL statements, migrations, repository code, services, or UI behavior.

## Product Boundary

NetworkOps V1 is a Personal Relationship Intelligence System.

People are the primary entity. All other entities exist to preserve useful context around people: ways to reach them, interactions with them, signals learned about them, possible opportunities involving them, and relationship links between them.

NetworkOps V1 is not:

- A note-taking application
- A personal wiki
- A general knowledge management system
- A task manager
- A CRM clone

Standalone notes are intentionally excluded from the V1 schema. Notes may belong to future Solo ecosystem modules, but they are not a NetOps V1 entity.

## Global Schema Conventions

### Storage Engine

SQLite is the target storage engine.

### Identifier Strategy

All primary entities use UUIDs stored as text.

UUIDs are the true identity of records. Human-readable values such as names, labels, emails, phone numbers, and social handles are attributes, not identity.

### Date And Time Strategy

Use text values for dates and timestamps.

- Date-only values use `YYYY-MM-DD`.
- Month-only known values may use `YYYY-MM` only when the field explicitly permits partial dates.
- Timestamps use ISO-8601 text with timezone or UTC convention.

The implementation should apply one consistent timestamp convention across the schema.

### Boolean Strategy

Boolean values should be stored as integer values:

- `0` means false.
- `1` means true.

### Long-Form Text Strategy

Long-form fields use unrestricted text storage.

The schema must not impose artificial length limits on long-form fields. The application must preserve line breaks, pasted paragraphs, bullets, and multiline formatting.

Long-form text fields include:

- `people.dossier`
- `people.origin_story`
- `people.importance_reason`
- `interactions.summary`
- `interactions.takeaways`
- `interactions.action_items`
- `signals.signal_text`
- `opportunities.description`
- `relationship_links.description`

SQLite `TEXT` storage is appropriate for these fields.

### Archive Strategy

Primary records should support soft archival where needed using `archived_at`.

Archival means the record remains stored but should be hidden from normal active views unless the user asks for archived records.

### Duplicate Strategy

Duplicate prevention is not required.

Potential duplicate people may exist. Future duplicate detection can compare names, contact methods, emails, phone numbers, LinkedIn, GitHub, and other social accounts. Duplicate detection should warn, not block creation.

## Entity Summary

Core V1 entities:

1. People
2. Contact Methods
3. Interactions
4. Signals
5. Opportunities
6. Relationship Links
7. Tags

Supporting relationship tables:

- `interaction_people`
- `opportunity_people`
- `taggings`

These supporting tables are part of the schema, but they exist only to connect core entities.

## 1. People

### Purpose

People are the center of NetworkOps. A person record preserves durable identity, relationship context, strategic context, contact-independent intelligence, and operational follow-up information.

Names are not unique. People are identified by `person_id`.

### Table

`people`

### Fields

#### `person_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for a person.

#### `name`

Type: Text  
Required: Yes  
Description: Primary display name for the person. This is required but not unique.

#### `alias`

Type: Text  
Required: No  
Description: Alternate name, nickname, shorthand, or preferred informal name.

#### `role`

Type: Text  
Required: No  
Description: Current role, title, or professional function.

#### `organization`

Type: Text  
Required: No  
Description: Current organization, company, school, team, group, or affiliation.

#### `location`

Type: Text  
Required: No  
Description: Location associated with the person.

#### `birthday`

Type: Text  
Required: No  
Description: Birthday or known birthday fragment. Prefer `YYYY-MM-DD` when full date is known.

#### `profile_photo_path`

Type: Text  
Required: No  
Description: Relative local file path or asset reference for the person's profile photo. The image itself is stored as a local file, not in the database.

#### `relationship_type`

Type: Text  
Required: No  
Description: User-facing relationship category such as mentor, peer, friend, family, recruiter, manager, or custom value. The value should remain extensible.

#### `relationship_status`

Type: Text  
Required: No  
Description: Current relationship state such as active, dormant, or archived. The value should be validated by application rules or controlled vocabulary.

#### `relationship_strength`

Type: Text  
Required: No  
Description: User-entered or controlled relationship strength indicator.

Design Note: V1 stores `relationship_strength` as text to preserve flexibility during early usage. Future versions may migrate relationship strength to a numeric scoring system. Numeric scoring would support ranking, filtering, analytics, and prioritization, but no numeric migration is required in V1.

#### `origin_story`

Type: Long text  
Required: No  
Description: Multiline description of how the relationship began or how the user met the person.

#### `importance_reason`

Type: Long text  
Required: No  
Description: Multiline explanation of why the person matters to the user's network or goals.

#### `dossier`

Type: Long text  
Required: No  
Description: General structured/freeform person intelligence summary.

#### `interests`

Type: Long text  
Required: No  
Description: Interests, topics, or areas the person cares about. Stored as text in V1 to preserve flexible entry.

#### `communication_style`

Type: Long text  
Required: No  
Description: Notes about how the person communicates or prefers to receive communication.

#### `preferences`

Type: Long text  
Required: No  
Description: Known preferences, working style, or relationship handling notes.

#### `current_goals`

Type: Long text  
Required: No  
Description: Known current goals, priorities, or areas of focus for the person.

#### `potential_value`

Type: Long text  
Required: No  
Description: Possible value, opportunity, mentorship, collaboration, introduction, or insight connected to the person.

#### `first_met`

Type: Text date  
Required: No  
Description: Date or approximate date when the user first met the person.

#### `last_contact`

Type: Text date  
Required: No  
Description: Most recent known contact date. This may be derived from interactions in implementation, but the schema allows storing it if needed for performance or migration compatibility.

#### `next_action`

Type: Text  
Required: No  
Description: Next known manual action related to the person. This is not a task system; it is lightweight relationship context.

#### `follow_up_date`

Type: Text date  
Required: No  
Description: Date when the user intends to follow up with the person.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the person was archived.

### Relationships

- One person has many contact methods.
- One person may participate in many interactions through `interaction_people`.
- One person may have many signals.
- One person may participate in many opportunities through `opportunity_people`.
- One person may have many relationship links to other people.
- One person may have many tags through `taggings`.

### Index Recommendations

- Index `people.name`.
- Index `people.organization`.
- Index `people.relationship_type`.
- Index `people.relationship_status`.
- Index `people.follow_up_date`.
- Index `people.archived_at`.

## 2. Contact Methods

### Purpose

Contact methods store structured ways to reach or identify a person. Email, phone, LinkedIn, GitHub, and other social accounts are attributes connected to a person, not identity.

### Table

`contact_methods`

### Fields

#### `contact_method_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the contact method.

#### `person_id`

Type: UUID text  
Required: Yes  
Description: Person this contact method belongs to.

#### `type`

Type: Text  
Required: Yes  
Description: Contact method type, such as email, phone, linkedin, github, or other_social. Values should be extensible.

#### `label`

Type: Text  
Required: No  
Description: User-facing label such as work, personal, primary, old, school, or custom.

#### `value`

Type: Text  
Required: Yes  
Description: User-facing contact value.

#### `normalized_value`

Type: Text  
Required: No  
Description: Comparison-friendly value used for duplicate detection and lookup.

#### `is_primary`

Type: Integer boolean  
Required: Yes  
Description: Whether this is the preferred contact method of its type for the person.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the contact method was archived.

### Relationships

- Many contact methods belong to one person.

### Index Recommendations

- Index `contact_methods.person_id`.
- Index `contact_methods.type`.
- Index `contact_methods.normalized_value`.
- Composite index on `contact_methods.person_id` and `contact_methods.type`.

## 3. Interactions

### Purpose

Interactions preserve conversations, meetings, calls, introductions, or other relationship touchpoints over time. They capture what happened and what was learned or promised.

Interactions must support multiple people.

### Table

`interactions`

### Fields

#### `interaction_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the interaction.

#### `interaction_date`

Type: Text date  
Required: Yes  
Description: Date when the interaction occurred.

#### `interaction_type`

Type: Text  
Required: No  
Description: Type of interaction, such as meeting, call, message, email, introduction, event, or custom.

#### `summary`

Type: Long text  
Required: No  
Description: Multiline summary of the interaction.

#### `takeaways`

Type: Long text  
Required: No  
Description: Multiline takeaways or lessons from the interaction.

#### `action_items`

Type: Long text  
Required: No  
Description: Multiline action items, commitments, or follow-up items from the interaction.

#### `sentiment`

Type: Text  
Required: No  
Description: Optional user-entered sentiment or tone indicator. Values should remain extensible.

#### `follow_up_required`

Type: Integer boolean  
Required: Yes  
Description: Whether the interaction created a follow-up need.

#### `follow_up_date`

Type: Text date  
Required: No  
Description: Date for follow-up related to the interaction.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the interaction was archived.

### Supporting Table

`interaction_people`

This table connects interactions to one or more people.

#### `interaction_person_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the interaction-person link.

#### `interaction_id`

Type: UUID text  
Required: Yes  
Description: Linked interaction.

#### `person_id`

Type: UUID text  
Required: Yes  
Description: Linked person.

#### `role`

Type: Text  
Required: No  
Description: Person's role in the interaction, such as participant, host, introducer, interviewer, interviewee, or custom.

#### `is_primary`

Type: Integer boolean  
Required: Yes  
Description: Whether this person is the primary person for display or legacy compatibility.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Link creation timestamp.

### Relationships

- One interaction has many linked people through `interaction_people`.
- One person has many interactions through `interaction_people`.
- One interaction may be the source of many signals.
- One interaction may be linked to opportunities through relationship links.

### Index Recommendations

- Index `interactions.interaction_date`.
- Index `interactions.follow_up_required`.
- Index `interactions.follow_up_date`.
- Index `interactions.archived_at`.
- Index `interaction_people.interaction_id`.
- Index `interaction_people.person_id`.
- Composite unique index on `interaction_people.interaction_id` and `interaction_people.person_id`.

## 4. Signals

### Purpose

Signals preserve relationship intelligence learned over time.

Use the term Signal for relationship intelligence in NetworkOps V1.

Examples:

- Values persistence
- Interested in AI
- Hiring soon
- Responds well to initiative

Signals may optionally reference an interaction as their source.

### Table

`signals`

### Fields

#### `signal_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the signal.

#### `person_id`

Type: UUID text  
Required: Yes  
Description: Person the signal is about.

#### `signal_text`

Type: Long text  
Required: Yes  
Description: Multiline signal text.

#### `confidence`

Type: Text  
Required: No  
Description: Confidence level such as low, medium, high, or custom.

#### `source_interaction_id`

Type: UUID text  
Required: No  
Description: Interaction that produced or supports the signal.

#### `source_description`

Type: Text  
Required: No  
Description: Human-readable source context when the source is not a specific interaction.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the signal was archived.

### Relationships

- Many signals belong to one person.
- One signal may reference one source interaction.
- One interaction may source many signals.
- Signals may be linked to opportunities or other records through relationship links in future use.

### Index Recommendations

- Index `signals.person_id`.
- Index `signals.source_interaction_id`.
- Index `signals.confidence`.
- Index `signals.created_at`.
- Index `signals.archived_at`.

## 5. Opportunities

### Purpose

Opportunities represent possible future actions or relationship openings.

Examples:

- Mock interview
- Referral
- Collaboration
- Portfolio review

Opportunities are not a general task manager. They preserve potential future value connected to people.

Opportunities must support multiple people.

### Table

`opportunities`

### Fields

#### `opportunity_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the opportunity.

#### `title`

Type: Text  
Required: Yes  
Description: Short title for the opportunity.

#### `status`

Type: Text  
Required: Yes  
Description: Current opportunity status such as open, pending, complete, closed, or custom.

#### `description`

Type: Long text  
Required: No  
Description: Multiline opportunity description.

#### `follow_up_date`

Type: Text date  
Required: No  
Description: Date when the user should review or follow up on the opportunity.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `closed_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the opportunity was closed or completed.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the opportunity was archived.

### Supporting Table

`opportunity_people`

This table connects opportunities to one or more people.

#### `opportunity_person_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the opportunity-person link.

#### `opportunity_id`

Type: UUID text  
Required: Yes  
Description: Linked opportunity.

#### `person_id`

Type: UUID text  
Required: Yes  
Description: Linked person.

#### `role`

Type: Text  
Required: No  
Description: Person's role in the opportunity, such as owner, sponsor, mentor, introducer, collaborator, reviewer, or custom.

#### `is_primary`

Type: Integer boolean  
Required: Yes  
Description: Whether this person is the primary person for display or legacy compatibility.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Link creation timestamp.

### Relationships

- One opportunity has many linked people through `opportunity_people`.
- One person has many opportunities through `opportunity_people`.
- Opportunities may link to interactions or signals through relationship links.

### Index Recommendations

- Index `opportunities.status`.
- Index `opportunities.follow_up_date`.
- Index `opportunities.archived_at`.
- Index `opportunity_people.opportunity_id`.
- Index `opportunity_people.person_id`.
- Composite unique index on `opportunity_people.opportunity_id` and `opportunity_people.person_id`.

## 6. Relationship Links

### Purpose

Relationship links store explicit connections between records. In V1, the most important use is person-to-person relationships.

Examples:

- Henry mentors Isaac.
- Benjamin works with Henry.
- Dr. Olav knows Benjamin.

Relationship types should remain extensible and should not be hardcoded into the database schema.

### Table

`relationship_links`

### Fields

#### `relationship_link_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the relationship link.

#### `source_entity_type`

Type: Text  
Required: Yes  
Description: Type of the source entity. V1 should support at minimum `person`, `interaction`, `signal`, and `opportunity`.

#### `source_entity_id`

Type: UUID text  
Required: Yes  
Description: UUID of the source entity.

#### `target_entity_type`

Type: Text  
Required: Yes  
Description: Type of the target entity. V1 should support at minimum `person`, `interaction`, `signal`, and `opportunity`.

#### `target_entity_id`

Type: UUID text  
Required: Yes  
Description: UUID of the target entity.

#### `relationship_type`

Type: Text  
Required: Yes  
Description: Extensible relationship label such as mentors, works_with, knows, introduced_by, mentioned_in, sourced_from, related_to, or custom.

#### `description`

Type: Long text  
Required: No  
Description: Human-readable context explaining why the link exists.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the relationship link was archived.

### Relationships

- Relationship links can connect person to person.
- Relationship links can connect person to interaction, signal, or opportunity when needed.
- Relationship links can connect interaction to signal or opportunity when useful.

The schema should support directional links. If a relationship must be displayed bidirectionally, the application can either query both source and target sides or create a second inverse link depending on later product rules.

### Index Recommendations

- Index `relationship_links.source_entity_type`.
- Index `relationship_links.source_entity_id`.
- Index `relationship_links.target_entity_type`.
- Index `relationship_links.target_entity_id`.
- Index `relationship_links.relationship_type`.
- Composite index on `relationship_links.source_entity_type` and `relationship_links.source_entity_id`.
- Composite index on `relationship_links.target_entity_type` and `relationship_links.target_entity_id`.
- Composite index on `relationship_links.source_entity_id`, `target_entity_id`, and `relationship_type`.

## 7. Tags

### Purpose

Tags provide flexible classification and discovery. Tags should not replace structured fields when a value has operational meaning.

Use structured fields for values such as relationship status, opportunity status, contact method type, and signal confidence.

Use tags for flexible labels such as cybersecurity, tmobile, mentor, leadership, or conference.

### Table

`tags`

### Fields

#### `tag_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the tag.

#### `name`

Type: Text  
Required: Yes  
Description: User-facing tag name.

#### `normalized_name`

Type: Text  
Required: Yes  
Description: Normalized tag name for comparison and duplicate reduction.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Record creation timestamp.

#### `updated_at`

Type: Timestamp text  
Required: Yes  
Description: Last record update timestamp.

#### `archived_at`

Type: Timestamp text  
Required: No  
Description: Timestamp when the tag was archived.

### Supporting Table

`taggings`

This table connects tags to entities.

#### `tagging_id`

Type: UUID text  
Required: Yes  
Description: Permanent unique identifier for the tag assignment.

#### `tag_id`

Type: UUID text  
Required: Yes  
Description: Linked tag.

#### `entity_type`

Type: Text  
Required: Yes  
Description: Tagged entity type. V1 should support `person`, `interaction`, `signal`, and `opportunity`.

#### `entity_id`

Type: UUID text  
Required: Yes  
Description: UUID of the tagged entity.

#### `created_at`

Type: Timestamp text  
Required: Yes  
Description: Tag assignment creation timestamp.

### Relationships

- One tag can be assigned to many entities.
- One entity can have many tags.
- Tags are many-to-many through `taggings`.

### Index Recommendations

- Unique index on `tags.normalized_name`.
- Index `taggings.tag_id`.
- Index `taggings.entity_type`.
- Index `taggings.entity_id`.
- Composite unique index on `taggings.tag_id`, `taggings.entity_type`, and `taggings.entity_id`.

## Relationship Design

### People And Contact Methods

One person has many contact methods.

Each contact method belongs to one person.

### People And Interactions

People and interactions are many-to-many.

Use `interaction_people` so one interaction can include multiple people.

### People And Signals

One person has many signals.

Each signal is about one primary person in V1.

If a signal eventually applies to multiple people, use relationship links rather than duplicating the signal text.

### People And Opportunities

People and opportunities are many-to-many.

Use `opportunity_people` so one opportunity can involve multiple people with different roles.

### Person-To-Person Relationships

Person-to-person relationships use `relationship_links`.

Relationship examples:

- Source person: Henry
- Relationship type: mentors
- Target person: Isaac

or:

- Source person: Benjamin
- Relationship type: works_with
- Target person: Henry

or:

- Source person: Dr. Olav
- Relationship type: knows
- Target person: Benjamin

Relationship types remain extensible text values. Do not hardcode relationship types into the schema.

## Integrity Rules

### Required Parent Records

- `contact_methods.person_id` must reference an existing person.
- `interaction_people.interaction_id` must reference an existing interaction.
- `interaction_people.person_id` must reference an existing person.
- `signals.person_id` must reference an existing person.
- `signals.source_interaction_id`, when present, must reference an existing interaction.
- `opportunity_people.opportunity_id` must reference an existing opportunity.
- `opportunity_people.person_id` must reference an existing person.
- `taggings.tag_id` must reference an existing tag.

### Polymorphic Link Validation

`relationship_links` and `taggings` use `entity_type` plus `entity_id` references.

SQLite cannot enforce polymorphic foreign keys directly without additional implementation choices. The schema implementation should enforce valid entity types and entity existence through application validation, triggers, or a later explicit link-table strategy.

For V1 schema design, allowed entity types are:

- `person`
- `interaction`
- `signal`
- `opportunity`

Tags and contact methods should not be relationship-link targets in V1 unless a later spec expands the scope.

### Delete And Archive Behavior

Prefer archival over hard delete for primary relationship intelligence records.

If hard delete is implemented later, it must not silently destroy related relationship intelligence. Delete behavior should be explicit in migrations and repository rules.

## Controlled And Extensible Values

Some fields should be structured enough for filtering, but still flexible enough for personal relationship data.

Recommended application-controlled fields:

- `contact_methods.type`
- `people.relationship_status`
- `people.relationship_type`
- `people.relationship_strength`
- `interactions.interaction_type`
- `interactions.sentiment`
- `signals.confidence`
- `opportunities.status`

Do not hardcode person-to-person relationship types in the database schema. `relationship_links.relationship_type` must remain extensible.

## Profile Photo Storage

Profile photos are not stored in the database.

The database stores only `people.profile_photo_path`.

Recommended asset location:

```text
data/
    assets/
        profile_photos/
```

The stored path should be relative to the app data root or asset root so the portable app folder can move across machines.

If a photo file is missing or unsupported, the person record must remain valid.

## Migration Compatibility Notes

The future migration from the current implementation to V1 should preserve existing records without manual cleanup.

Expected mapping direction:

- Existing people become `people`.
- Existing email, phone, and social-like values become `contact_methods`.
- Existing interactions become `interactions`.
- Existing interaction-person references become `interaction_people`.
- Existing signals remain `signals`.
- Existing open-loop or opportunity-like records may become `opportunities` only when they represent future relationship value, not generic tasks.
- Existing relationship records may become `relationship_links`.
- Existing person tags may become `tags` and `taggings`.
- Existing standalone notes should not become a standalone V1 entity. If preservation is required, migrate person-specific note content into the closest person, interaction, signal, opportunity, or archival compatibility field chosen by the migration plan.

This document does not define the migration plan.

## Schema Readiness Checklist

Before implementation, confirm:

- People use UUID identity.
- Name is required but not unique.
- Contact methods are separate from people.
- Interactions support multiple people through `interaction_people`.
- Signals remain the V1 term for relationship intelligence.
- Opportunities support multiple people through `opportunity_people`.
- Relationship links support person-to-person relationships.
- Relationship types remain extensible.
- Standalone notes are not included.
- Long-form fields use unrestricted text.
- Profile photos are local files referenced by path.
- Duplicate detection does not block record creation.
- Tags are flexible discovery labels, not replacements for structured fields.

## Non-Goals

The V1 schema does not include:

- Standalone notes
- AI
- Semantic search
- Graph visualization
- Automation
- Recommendation systems
- Voice interfaces
- Obsidian integration
- Notion integration
- Gmail or calendar integration
- CRM synchronization
- Solo module data tables

## Schema Cleanup Summary

### Changes Applied

- Removed `people.mutual_connections`.
- Confirmed relationship intelligence between people should come from `relationship_links`, not duplicated long-form person fields.
- Added a design note for `people.relationship_strength` explaining that V1 stores it as text and future versions may migrate to numeric scoring for ranking, filtering, analytics, and prioritization.

### Concerns Found

- `people.mutual_connections` conflicted with the relationship-link strategy by creating a second source of truth for person-to-person relationship context. This was removed.
- No other clear architectural conflicts were found during this cleanup pass.
- Several fields remain intentionally flexible text values, including `relationship_type`, `relationship_strength`, `interaction_type`, `sentiment`, `signals.confidence`, and `opportunities.status`. This is consistent with the current ADRs as long as application validation or controlled vocabularies are defined during implementation.

### Recommended Follow-Up Before Implementation

- Decide whether controlled values are enforced through application validation, SQLite `CHECK` constraints, or lookup tables.
- Decide exact timestamp format and timezone convention.
- Decide whether `people.last_contact` is stored, derived, or maintained as a cached value.
- Define migration mapping from existing relationship, note, open-loop, and dossier fields into the V1 schema without reintroducing duplicate relationship sources of truth.
