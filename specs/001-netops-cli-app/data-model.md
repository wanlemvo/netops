> Historical design record; not current product instructions. See the [current README](../../README.md).

# Data Model: NetOps CLI App

## Person

Represents a contact tracked by the user.

**Fields**:
- `id`: stable unique identifier
- `display_name`: required human-readable name
- `given_name`: optional first name
- `family_name`: optional last name
- `primary_email`: optional email address
- `primary_phone`: optional phone number
- `organization`: optional organization or group context
- `tags`: zero or more labels
- `relationship_notes`: optional freeform context
- `created_at`: creation timestamp
- `updated_at`: last update timestamp

**Relationships**:
- Has many interactions
- Has many open loops
- Has many suggested actions
- Has many evaluations through actions and interactions
- Can participate in many relationship records

**Validation rules**:
- `display_name` is required and cannot be blank.
- Email and phone are optional but must be stored consistently when supplied.
- Duplicate names are allowed, but the directory must expose enough context to distinguish them.

## Relationship

Represents a described connection involving a person.

**Fields**:
- `id`: stable unique identifier
- `person_id`: required person reference
- `related_person_id`: optional second person reference
- `relationship_type`: required category, such as colleague, friend, mentor, client, family, or custom
- `strength`: optional user-selected value or note
- `notes`: optional context
- `created_at`: creation timestamp
- `updated_at`: last update timestamp

**Relationships**:
- Belongs to one primary person
- Optionally links two tracked people

**Validation rules**:
- A relationship must reference an existing person.
- `relationship_type` is required.
- A person cannot be related to themselves through `related_person_id`.

## Interaction

Represents a logged event with a person.

**Fields**:
- `id`: stable unique identifier
- `person_id`: required person reference
- `occurred_on`: required date or datetime
- `interaction_type`: required category, such as call, message, meeting, email, note, or custom
- `notes`: required freeform notes
- `created_at`: creation timestamp
- `updated_at`: last update timestamp

**Relationships**:
- Belongs to one person
- Can create or reference open loops
- Can be referenced by evaluations

**Validation rules**:
- Interaction must reference an existing person.
- `occurred_on`, `interaction_type`, and `notes` are required.
- Future dates require a confirmation path in user-facing workflows.

## Open Loop

Represents an unresolved commitment, topic, or follow-up.

**Fields**:
- `id`: stable unique identifier
- `person_id`: required person reference
- `source_interaction_id`: optional interaction reference
- `description`: required action or unresolved topic
- `status`: one of `open`, `completed`, `deferred`, `closed_no_action`
- `due_on`: optional due date
- `priority`: optional user priority
- `resolution_notes`: optional notes when closed
- `created_at`: creation timestamp
- `updated_at`: last update timestamp
- `closed_at`: optional close timestamp

**Relationships**:
- Belongs to one person
- Optionally originates from one interaction
- Can drive suggested actions

**State transitions**:
- `open` -> `completed`
- `open` -> `deferred`
- `open` -> `closed_no_action`
- `deferred` -> `open`
- `deferred` -> `completed`
- Closed states preserve history and are not deleted by default.

**Validation rules**:
- `description` is required.
- `status` must be a known value.
- `closed_at` is required when status is completed or closed without action.

## Suggested Action

Represents a generated next step.

**Fields**:
- `id`: stable unique identifier
- `person_id`: required person reference
- `open_loop_id`: optional open-loop reference
- `action_text`: required suggested action
- `reason`: required explanation
- `priority_score`: required numeric score
- `status`: one of `new`, `accepted`, `ignored`, `completed`
- `generated_at`: generation timestamp
- `acted_at`: optional timestamp when accepted, ignored, or completed

**Relationships**:
- Belongs to one person
- May be tied to one open loop
- May have one or more evaluations after completion

**State transitions**:
- `new` -> `accepted`
- `new` -> `ignored`
- `accepted` -> `completed`
- `accepted` -> `ignored`

**Validation rules**:
- `action_text` and `reason` are required.
- Suggestions must be reproducible from persisted history or stored when acted upon.

## Evaluation

Represents the user's review of an action or interaction outcome.

**Fields**:
- `id`: stable unique identifier
- `person_id`: required person reference
- `suggested_action_id`: optional suggested-action reference
- `interaction_id`: optional interaction reference
- `outcome`: one of `positive`, `neutral`, `negative`, `unknown`
- `impact_notes`: optional freeform notes
- `evaluated_on`: required date
- `created_at`: creation timestamp

**Relationships**:
- Belongs to one person
- References either a suggested action, an interaction, or both

**Validation rules**:
- At least one of `suggested_action_id` or `interaction_id` is required.
- `outcome` and `evaluated_on` are required.

## Suggestion Scoring Inputs

The suggestion engine uses derived facts rather than a separate persisted entity.

**Inputs**:
- Overdue open loops
- Due-soon open loops
- Last interaction date per person
- Open-loop age
- Prior evaluation outcomes
- Relationship tags or categories
- Recently ignored suggestions

**Validation rules**:
- Every displayed suggestion must include at least one reason traceable to stored records.
- Ignored suggestions should reduce repeat frequency unless the underlying open loop becomes urgent.
