> Historical design record; not current product instructions. See the [current README](../../README.md).

# Feature Specification: NetworkOps Person Intelligence Record

**Feature Branch**: `004-person-intelligence-record`  
**Created**: 2026-06-04  
**Status**: Draft  
**Input**: User description: "Refactor NetworkOps from a basic contact tracker into a person intelligence record system with separate entities for people, interaction logs, notes, signals, and opportunities. Address profile photos, real email and phone fields, text entry limits, and multiline note entry."

## Problem Statement

Traditional contact managers preserve contact information but fail to preserve relationship context. They can store a name, email, phone number, and company, but they usually lose the story of why the relationship matters, what commitments were made, what opportunities are open, what lessons were learned, and what signals emerged over time. As a result, relationship intelligence decays between interactions, and useful context must be reconstructed manually instead of carried forward by the system.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture a complete person intelligence record (Priority: P1)

As a NetworkOps user, I want each person record to capture identity, contact methods, relationship context, dossier intelligence, strategic context, operational follow-up, and organization tags so that a person profile becomes actionable relationship intelligence instead of a static contact card.

**Why this priority**: This is the core V1 shift from contact tracking to person intelligence. Without the expanded record, later logs, signals, opportunities, and follow-up workflows do not have a useful center of gravity.

**Independent Test**: Can be fully tested by creating or editing a person record with the V1 schema fields, saving the record, reopening it, and confirming every entered value remains readable and editable.

**Acceptance Scenarios**:

1. **Given** no existing person record for Harper Vale, **When** the user creates a new person with name, role, organization, contact methods, relationship context, dossier details, strategic context, next action, follow-up date, and tags, **Then** the saved profile displays those values in a coherent person intelligence record.
2. **Given** an existing person record, **When** the user edits any V1 field and saves, **Then** the updated value appears when the profile is reopened and no unrelated fields are changed.
3. **Given** a user only knows the person's name, **When** the user creates the record with all other fields blank, **Then** the system saves the person and clearly treats missing optional fields as unset instead of invalid.

---

### User Story 2 - Store usable contact methods and profile photos (Priority: P1)

As a NetworkOps user, I want people to have explicit email, phone, social, and profile photo fields so that their information can be displayed, searched, reused, and eventually connected to reminders, exports, or automation.

**Why this priority**: Contact methods and profile photos are basic usability requirements for a person intelligence record. Treating them as generic notes prevents the system from using them later.

**Independent Test**: Can be fully tested by adding a profile photo and multiple contact methods to a person, saving the record, reopening the record, and confirming the image and contact values remain attached to the correct person.

**Acceptance Scenarios**:

1. **Given** a person record, **When** the user adds an email address and phone number, **Then** those values are displayed as dedicated contact method fields.
2. **Given** a person record, **When** the user adds LinkedIn, GitHub, and other social information, **Then** each value is preserved as contact data rather than being merged into freeform notes.
3. **Given** a person record, **When** the user uploads or assigns a profile photo, **Then** the photo is displayed with that person's record and remains available after the app is restarted.

---

### User Story 3 - Enter long and multiline intelligence without losing data (Priority: P1)

As a NetworkOps user, I want long text fields to support pasted text, wrapping, scrolling, and multiline formatting so that notes, dossiers, origin stories, and interaction summaries can capture real context.

**Why this priority**: The current text entry behavior blocks the primary value of the app. Relationship intelligence depends on nuanced text, and the system must not reject content just because it is longer than the visible window.

**Independent Test**: Can be fully tested by pasting a long multiline note into each long-form field, saving it, reopening it, and confirming the full text and line breaks are preserved.

**Acceptance Scenarios**:

1. **Given** a long-form field such as dossier or origin story, **When** the user pastes text longer than the visible entry area, **Then** the full text is accepted, stored, and available for review.
2. **Given** a long-form field, **When** the user presses Enter to create line breaks, **Then** the field supports multiline content rather than prematurely submitting or blocking input.
3. **Given** a long-form value that does not fit on screen, **When** the user views or edits it, **Then** the user can navigate through the full value without losing text.

---

### User Story 4 - Separate people from logs, notes, signals, and opportunities (Priority: P2)

As a NetworkOps user, I want interaction logs, personal notes, signals, and opportunities to be separate entities from the person profile so that each type of intelligence can grow over time without cluttering the core person record.

**Why this priority**: The person record should summarize durable intelligence, while event-based and action-based information should live in objects that can be linked, reviewed, and expanded independently.

**Independent Test**: Can be fully tested by creating a person, adding an interaction log, a note, a signal, and an opportunity, then confirming each object can be viewed independently while remaining linked to the relevant person where appropriate.

**Acceptance Scenarios**:

1. **Given** a person record, **When** the user records a meeting summary with takeaways and action items, **Then** the entry is saved as an interaction log linked to the person rather than being flattened into the person profile.
2. **Given** the user creates a general note not tied to one person, **When** the note is saved, **Then** it remains accessible as a standalone note with title, content, tags, and creation date.
3. **Given** the user identifies a signal such as "Henry values persistence", **When** the signal is saved, **Then** it can include confidence and source context and can be linked back to its source.
4. **Given** the user creates an opportunity such as "Mock Interview", **When** it is saved, **Then** it has title, owner, status, description, and follow-up date separate from the person's profile fields.

---

### User Story 5 - Turn relationship data into next actions (Priority: P2)

As a NetworkOps user, I want each person record and opportunity to surface next action and follow-up timing so that the system helps me maintain relationships instead of only storing information.

**Why this priority**: NetworkOps becomes useful when it supports action. Follow-up fields turn passive records into operational reminders and open loops.

**Independent Test**: Can be fully tested by adding next actions and follow-up dates to people and opportunities, then confirming they are visible in the record and available for review as pending work.

**Acceptance Scenarios**:

1. **Given** a person has a next action and follow-up date, **When** the user views that person, **Then** the next action and follow-up date are clearly visible.
2. **Given** an opportunity has a follow-up date, **When** the user reviews opportunities, **Then** the opportunity can be identified as open, pending, or complete.

### Edge Cases

- A user creates a person with only a required name and no other known information.
- A user pastes long text containing line breaks, bullets, quotes, URLs, or paragraphs into a long-form field.
- A user resizes the app window or uses a small terminal while viewing or editing long text.
- A user adds duplicate contact methods or leaves contact fields blank.
- A profile photo file is moved, renamed, missing, or unsupported after being assigned.
- A signal or opportunity references a person that is later deleted or archived.
- A general note has no person association.
- A follow-up date is blank, invalid, or in the past.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a V1 person record with these sections: Identity, Contact Methods, Relationship, Dossier, Strategic Context, Network Ops, and Organization.
- **FR-002**: System MUST require `name` for every person record.
- **FR-003**: System MUST treat all other V1 person fields as optional.
- **FR-004**: System MUST support Identity fields for name, alias, role, organization, location, and birthday.
- **FR-005**: System MUST support dedicated Contact Method fields for email, phone, LinkedIn, GitHub, and other social links or handles.
- **FR-006**: System MUST support assigning and displaying a profile photo for a person.
- **FR-007**: System MUST support Relationship fields for relationship type, relationship strength, origin story, and importance reason.
- **FR-008**: System MUST support Dossier fields for dossier, interests, communication style, preferences, and signals summary.
- **FR-009**: System MUST support Strategic Context fields for current goals, potential value, and mutual connections.
- **FR-010**: System MUST support Network Ops fields for first met, last contact, next action, and follow-up date.
- **FR-011**: System MUST support Organization fields for tags.
- **FR-012**: System MUST preserve long-form text beyond the visible window width or height.
- **FR-013**: System MUST preserve multiline formatting in long-form fields.
- **FR-014**: System MUST allow pasted text in long-form fields without truncating content because of visible screen size.
- **FR-015**: System MUST distinguish short single-value fields from long-form fields that need multiline editing.
- **FR-016**: System MUST model interaction logs as separate records with date, person association, summary, takeaways, action items, sentiment, and follow-up required status.
- **FR-017**: System MUST model notes as separate records with title, content, tags, and creation date, and notes MUST NOT require association with a single person.
- **FR-018**: System MUST model signals as separate records with signal text, confidence, source, and optional person association.
- **FR-019**: System MUST model opportunities as separate records with title, owner or linked person, status, description, and follow-up date.
- **FR-020**: System MUST allow people to be linked to interaction logs, signals, and opportunities without embedding every related object directly into the person record.
- **FR-021**: System MUST display missing optional data consistently as empty or unset without implying an error.
- **FR-022**: System MUST allow records created before V1 to remain accessible after the schema changes.
- **FR-023**: System MUST support reviewing pending next actions and follow-ups from person and opportunity data.

### Key Entities *(include if feature involves data)*

- **Person**: The central person intelligence record. Key attributes include identity, contact methods, relationship context, dossier intelligence, strategic context, network operations fields, tags, and optional profile photo.
- **Contact Method**: Structured ways to reach or identify a person, including email, phone, LinkedIn, GitHub, and other social channels.
- **Interaction Log**: A dated event or conversation associated with a person. Captures summary, takeaways, action items, sentiment, and whether follow-up is required.
- **Note**: A user-authored note that may be general or loosely tagged, not necessarily tied to one person.
- **Signal**: An observed pattern, belief, preference, value, or piece of intelligence with confidence and source context.
- **Opportunity**: A possible relationship action or opening, such as a mock interview, introduction, mentorship path, referral, or meeting.
- **Relationship Link**: A connection between a person and related records such as logs, signals, notes, opportunities, or future graph relationships.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can create a complete V1 person intelligence record in under 5 minutes when the information is already available.
- **SC-002**: 100% of V1 person fields entered by the user remain visible and editable after saving and reopening the app.
- **SC-003**: A user can paste at least 2,000 characters of multiline text into long-form fields without truncation or loss of line breaks.
- **SC-004**: A user can add and later view at least one profile photo, email, phone number, and social link for a person.
- **SC-005**: A user can create at least one interaction log, note, signal, and opportunity without storing them as plain person-profile text.
- **SC-006**: Existing person records remain viewable after the V1 schema change with no required manual data cleanup.
- **SC-007**: A user can identify the next action and follow-up date for a person or opportunity in under 30 seconds.

## Assumptions

- NetworkOps V1 remains local-first and single-user unless a future feature expands collaboration.
- The person record is the primary navigation center, but interaction logs, notes, signals, and opportunities are separate data concepts.
- Name is the only required field for a person because real relationship intelligence is often gathered gradually.
- Email and phone should be structured enough to reuse later, while still allowing imperfect or partial information during early capture.
- Profile photos are user-supplied local assets and should remain available when the portable app folder is moved, as long as the app's data folder is moved with it.
- Long-form fields include origin story, importance reason, dossier, interests, communication style, preferences, signals, current goals, potential value, mutual connections, interaction summaries, takeaways, action items, note content, signal text, and opportunity descriptions.
- V1 should not require automated AI analysis, graph visualization, or external integrations, though the model should leave room for those later.

## Future Considerations

These items clarify the long-term product and architecture direction for NetworkOps. They are intentionally not part of the V1 implementation scope unless a later specification promotes them into requirements.

- **Natural language entry**: Future versions may allow users to capture relationship updates in plain language and have the system assist with organizing that input into the appropriate person fields, logs, signals, notes, or opportunities.
- **Controlled vocabularies and selectable fields**: Future versions may introduce selectable values for fields such as relationship type, relationship strength, sentiment, confidence, opportunity status, and tags to improve consistency without removing freeform capture where it matters.
- **Cross-linking between entities**: Future versions may allow people, interaction logs, notes, signals, opportunities, and relationship records to reference each other directly so context can move across the system instead of living in isolated records.
- **Multiple participants per interaction**: Future versions may support interaction logs involving more than one person, allowing a single meeting, call, introduction, or event to connect multiple people and downstream follow-ups.
- **Backlinks**: Future versions may show reverse references so a person, note, signal, or opportunity can reveal which records mention or depend on it.
- **Knowledge graph architecture**: Future versions may evolve the data model toward graph-like relationships where people, organizations, signals, opportunities, notes, and interactions are connected through explicit links.
- **Future Solo module integration**: Future versions may integrate NetworkOps with a Solo module so relationship intelligence can connect to broader personal operating-system workflows such as goals, projects, decisions, learning, and execution planning.
