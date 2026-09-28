# Contract: NetworkOps V1 Data Behavior

## Scope

This contract defines expected data behavior for the NetworkOps V1 schema implementation.

## Person Records

- Creating a person requires `name`.
- Person names are not unique.
- Person IDs are UUID text values.
- Creating duplicate-looking people is allowed.
- Missing optional fields display as empty or unset without error.
- `mutual_connections` must not exist as a person field.

## Contact Methods

- A person can have multiple contact methods.
- Contact methods require person, type, value, and timestamps.
- Email, phone, LinkedIn, GitHub, and other social values are stored as contact methods, not person columns.
- Duplicate-looking contact methods may warn in future but must not block creation in V1.

## Interactions

- Interactions can link to multiple people.
- An interaction is connected to people through `interaction_people`.
- Long-form fields preserve line breaks and pasted text.
- Interactions may source signals.

## Signals

- Signals are separate records.
- A signal belongs to one primary person.
- A signal may reference a source interaction.
- Signal text is required.

## Opportunities

- Opportunities can link to multiple people.
- An opportunity is connected to people through `opportunity_people`.
- Opportunity title and status are required.
- Opportunity descriptions preserve multiline text.
- Opportunities represent potential relationship value, not generic tasks.

## Relationship Links

- Relationship links support person-to-person relationships.
- Relationship types are extensible.
- Relationship links may connect people, interactions, signals, and opportunities.
- Relationship links must use stable entity IDs, not names.

## Tags

- Tags are optional flexible discovery labels.
- Tags must not replace structured fields such as relationship status, opportunity status, or signal confidence.

## Out Of Scope

- Standalone notes
- AI
- Semantic search
- Graph visualization
- Automation
- Recommendation systems
- Voice interfaces
