# Data Model: NetworkOps Person Intelligence Record

This feature data model follows the approved schema in `docs/schema_v1.md`.

Standalone notes are intentionally excluded from NetOps V1.

## Person

Primary entity for relationship intelligence.

**Fields**:

- `person_id`: UUID text, required, stable identity.
- `name`: text, required, display name, not unique.
- `alias`: text, optional.
- `role`: text, optional.
- `organization`: text, optional.
- `location`: text, optional.
- `birthday`: text date, optional.
- `profile_photo_path`: text, optional local asset reference.
- `relationship_type`: text, optional extensible category.
- `relationship_status`: text, optional controlled/application-validated value.
- `relationship_strength`: text, optional; V1 stores text, future numeric scoring may be introduced later.
- `origin_story`: long text, optional.
- `importance_reason`: long text, optional.
- `dossier`: long text, optional.
- `interests`: long text, optional.
- `communication_style`: long text, optional.
- `preferences`: long text, optional.
- `current_goals`: long text, optional.
- `potential_value`: long text, optional.
- `first_met`: text date, optional.
- `last_contact`: text date, optional or derived/cached by implementation.
- `next_action`: text, optional.
- `follow_up_date`: text date, optional.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Has many contact methods.
- Participates in many interactions through `interaction_people`.
- Has many signals.
- Participates in many opportunities through `opportunity_people`.
- Connects to other people and records through relationship links.
- May have tags through `taggings`.

**Validation rules**:

- `name` is required and cannot be blank.
- `name` is not unique.
- `mutual_connections` is not allowed; person-to-person context belongs in `relationship_links`.
- Profile photo path must not prevent opening the record if the file is missing.

## Contact Method

Structured way to reach or identify a person.

**Fields**:

- `contact_method_id`: UUID text, required.
- `person_id`: UUID text, required.
- `type`: text, required, extensible value such as email, phone, linkedin, github, other_social.
- `label`: text, optional.
- `value`: text, required.
- `normalized_value`: text, optional comparison-friendly value.
- `is_primary`: integer boolean, required.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Belongs to one person.

**Validation rules**:

- Contact method must reference an existing person.
- Duplicate-looking values are allowed but may produce future warnings.

## Interaction

Relationship touchpoint such as a meeting, call, message, introduction, or event.

**Fields**:

- `interaction_id`: UUID text, required.
- `interaction_date`: text date, required.
- `interaction_type`: text, optional.
- `summary`: long text, optional.
- `takeaways`: long text, optional.
- `action_items`: long text, optional.
- `sentiment`: text, optional.
- `follow_up_required`: integer boolean, required.
- `follow_up_date`: text date, optional.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Has many people through `interaction_people`.
- May source many signals.
- May link to opportunities through relationship links.

**Validation rules**:

- Must have at least one linked person before being considered complete.
- Long-form text must preserve line breaks and pasted content.

## Interaction Person

Join table linking interactions to people.

**Fields**:

- `interaction_person_id`: UUID text, required.
- `interaction_id`: UUID text, required.
- `person_id`: UUID text, required.
- `role`: text, optional.
- `is_primary`: integer boolean, required.
- `created_at`: timestamp text, required.

**Validation rules**:

- Interaction/person pairs should not be duplicated.
- At most one primary participant should be selected for display/legacy compatibility unless implementation explicitly supports more.

## Signal

Relationship intelligence learned over time.

**Fields**:

- `signal_id`: UUID text, required.
- `person_id`: UUID text, required.
- `signal_text`: long text, required.
- `confidence`: text, optional.
- `source_interaction_id`: UUID text, optional.
- `source_description`: text, optional.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Belongs to one primary person.
- May reference one source interaction.
- May link to opportunities or interactions through relationship links.

**Validation rules**:

- `signal_text` is required.
- Source interaction, when supplied, must exist.

## Opportunity

Possible future action or relationship opening.

**Fields**:

- `opportunity_id`: UUID text, required.
- `title`: text, required.
- `status`: text, required.
- `description`: long text, optional.
- `follow_up_date`: text date, optional.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `closed_at`: timestamp text, optional.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Has many people through `opportunity_people`.
- May link to interactions or signals through relationship links.

**Validation rules**:

- `title` is required.
- `status` must be application-valid.
- Opportunity should not become a generic task; it must preserve potential relationship value.

## Opportunity Person

Join table linking opportunities to people.

**Fields**:

- `opportunity_person_id`: UUID text, required.
- `opportunity_id`: UUID text, required.
- `person_id`: UUID text, required.
- `role`: text, optional.
- `is_primary`: integer boolean, required.
- `created_at`: timestamp text, required.

**Validation rules**:

- Opportunity/person pairs should not be duplicated.
- Roles remain extensible.

## Relationship Link

Explicit link between records, especially person-to-person relationships.

**Fields**:

- `relationship_link_id`: UUID text, required.
- `source_entity_type`: text, required.
- `source_entity_id`: UUID text, required.
- `target_entity_type`: text, required.
- `target_entity_id`: UUID text, required.
- `relationship_type`: text, required.
- `description`: long text, optional.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Can connect person to person.
- Can connect person to interaction, signal, or opportunity.
- Can connect interaction to signal or opportunity.

**Validation rules**:

- Allowed entity types in V1: `person`, `interaction`, `signal`, `opportunity`.
- Relationship types are extensible and not hardcoded.
- Entity existence must be validated by the application or storage layer because polymorphic foreign keys are not directly enforced by SQLite.

## Tag

Flexible discovery label.

**Fields**:

- `tag_id`: UUID text, required.
- `name`: text, required.
- `normalized_name`: text, required.
- `created_at`: timestamp text, required.
- `updated_at`: timestamp text, required.
- `archived_at`: timestamp text, optional.

**Relationships**:

- Has many taggings.

**Validation rules**:

- `normalized_name` should be unique.
- Tags must not replace structured fields for operational values.

## Tagging

Join table assigning tags to entities.

**Fields**:

- `tagging_id`: UUID text, required.
- `tag_id`: UUID text, required.
- `entity_type`: text, required.
- `entity_id`: UUID text, required.
- `created_at`: timestamp text, required.

**Validation rules**:

- Allowed entity types in V1: `person`, `interaction`, `signal`, `opportunity`.
- Duplicate tag assignments should be prevented.

## State And Lifecycle

- Primary records support archival with `archived_at`.
- Hard delete should be explicit and should not silently destroy relationship intelligence.
- Duplicate people are allowed; duplicate detection warns but does not block creation.
- Profile photos are local assets referenced from person records.
- Long-form text must be stored and reloaded without truncation.
