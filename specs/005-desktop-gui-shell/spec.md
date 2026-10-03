> Historical design record; not current product instructions. See the [current README](../../README.md).

# Feature Specification: NetworkOps Desktop GUI Shell

**Feature Branch**: `005-desktop-gui-shell`  
**Created**: 2026-06-13  
**Status**: Draft  
**Input**: User description: "Build a desktop GUI shell for NetworkOps based on the existing dossier mockup. The GUI should turn NetworkOps from a terminal-first prototype into a desktop app interface while using the existing backend service layer as the source of truth. The app should be local-first and portable, launch from a Windows executable, preserve data inside the portable app folder, include sidebar navigation, overview, people directory, person dossier view, profile photos, contact methods, interaction timeline, signals, opportunities, relationship links, open loops/follow-ups, create/edit workflows, multiline long-form editing, and avoid AI, semantic search, graph visualization, cloud sync, automation, or external integrations."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open and Browse the Desktop App (Priority: P1)

As a NetworkOps user, I want to launch the app from a desktop executable and navigate through a visual interface so that I can inspect my relationship intelligence without remembering terminal commands.

**Why this priority**: This is the core value of the feature: turning the current terminal-first prototype into a usable desktop app surface.

**Independent Test**: Can be fully tested by launching the app, using the sidebar to move between overview, people, and dossier views, and confirming that existing records are visible without entering commands.

**Acceptance Scenarios**:

1. **Given** the user has a portable NetworkOps folder, **When** they launch the desktop executable, **Then** the app opens to a visual interface with sidebar navigation and an overview view.
2. **Given** existing person records are stored locally, **When** the user opens the people directory and selects a person, **Then** the app displays that person's dossier without requiring terminal commands.
3. **Given** the local data store is empty, **When** the user launches the app, **Then** the app displays an empty-state experience with a clear path to create the first person record.

---

### User Story 2 - Review a Person Dossier (Priority: P1)

As a NetworkOps user, I want each person to open into a dossier-style screen so that I can quickly understand who they are, how to contact them, what I know about them, and what actions may be next.

**Why this priority**: The dossier is the primary NetworkOps experience and the strongest connection to the existing mockup direction.

**Independent Test**: Can be fully tested by opening a person with contacts, interactions, signals, opportunities, links, and profile data, then confirming that all sections are visible and readable.

**Acceptance Scenarios**:

1. **Given** a person has identity, contact, relationship, strategic, and network-ops data, **When** the user opens the dossier, **Then** the app presents those details in structured visual sections.
2. **Given** a person has interactions, signals, opportunities, relationship links, and follow-ups, **When** the user views the dossier, **Then** the app displays those contextual records in their appropriate dossier sections.
3. **Given** a person has a profile photo path, **When** the dossier is opened, **Then** the app displays the profile photo or a polished fallback when the photo is missing or unsupported.

---

### User Story 3 - Create and Edit Person Intelligence (Priority: P2)

As a NetworkOps user, I want to create and edit person records through visual forms so that I can maintain relationship intelligence without typing command flags or losing long-form context.

**Why this priority**: The app must become genuinely usable as a desktop workflow, not only a read-only viewer.

**Independent Test**: Can be fully tested by creating a person, adding contact methods, entering multiline dossier text, saving changes, closing and reopening the app, and confirming the data persists.

**Acceptance Scenarios**:

1. **Given** the user opens the create-person workflow, **When** they enter a name and optional fields, **Then** the app creates the person and opens the resulting dossier.
2. **Given** the user edits long-form fields such as dossier, origin story, importance reason, takeaways, action items, signals, or opportunity descriptions, **When** they use line breaks and save, **Then** the app preserves the full multiline text exactly enough to remain readable and useful.
3. **Given** the user adds contact methods, **When** they save email, phone, social, or other contact values, **Then** those contact methods appear in the dossier contact section and remain available after restart.

---

### User Story 4 - Manage Relationship Context (Priority: P3)

As a NetworkOps user, I want to add and review interactions, signals, opportunities, relationship links, and follow-ups from the desktop app so that the dossier remains actionable instead of becoming a static contact page.

**Why this priority**: Relationship context is what separates NetworkOps from a basic contact manager.

**Independent Test**: Can be fully tested by adding an interaction, signal, opportunity, relationship link, and follow-up from the GUI, then confirming each appears in the correct dossier section and overview context.

**Acceptance Scenarios**:

1. **Given** the user is viewing a person dossier, **When** they add an interaction log with summary, takeaways, and action items, **Then** the interaction appears in the person's timeline.
2. **Given** the user records a signal about a person, **When** they save it with optional confidence and source context, **Then** the signal appears in the signal ledger for that person.
3. **Given** the user creates an opportunity or relationship link involving one or more people, **When** they save it, **Then** the related dossier sections show the new context without duplicating person data.

---

### User Story 5 - Preserve Portable Local Data (Priority: P3)

As a NetworkOps user, I want the desktop app to remain local-first and portable so that I can move the app folder between machines and keep my data with it.

**Why this priority**: Portability is central to how the user wants to run and preserve the prototype.

**Independent Test**: Can be fully tested by launching the app from a portable folder, creating or editing data, closing the app, moving or copying the folder, and confirming the same data appears when launched from the copied folder.

**Acceptance Scenarios**:

1. **Given** the app is running from a portable folder, **When** the user creates or edits records, **Then** the data is stored inside the portable app folder.
2. **Given** the portable folder is copied to another compatible Windows machine, **When** the user launches the executable from that folder, **Then** the previously saved records remain available.
3. **Given** the app cannot access its local data folder, **When** it launches, **Then** it displays a clear error explaining that local data could not be opened.

### Edge Cases

- The app opens with no people records yet.
- A person has no contacts, interactions, signals, opportunities, relationship links, or profile photo.
- A stored profile photo path points to a file that no longer exists.
- Long-form text is larger than the visible editing area and requires scrolling.
- Pasted text contains line breaks, tabs, long URLs, or long unbroken words.
- The app window is smaller than the designed layout and must remain usable without overlapping text or controls.
- A create or edit form contains invalid or missing required data.
- Multiple people have similar names and must remain distinct records.
- The local data folder cannot be read or written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a desktop app shell that launches from a Windows executable.
- **FR-002**: The system MUST provide sidebar navigation for at least overview, people directory, dossier, open loops/follow-ups, and archive-style views.
- **FR-003**: The system MUST provide an overview/dashboard view showing high-level system state, recent intelligence, and follow-up context.
- **FR-004**: The system MUST provide a people directory that allows users to browse and select person records.
- **FR-005**: The system MUST provide a person dossier view following the dark, structured visual direction of the approved mockup.
- **FR-006**: The dossier view MUST display identity records, contact records, known profile information, relationship context, timeline/intel history, dossier folders, and actionable next-context sections when data exists.
- **FR-007**: The system MUST display profile photos when available and display a polished fallback when the photo is missing or unsupported.
- **FR-008**: The system MUST display and allow management of contact methods, including email, phone, social profiles, and other contact values.
- **FR-009**: The system MUST display and allow management of interaction logs, including summaries, takeaways, action items, sentiment, and follow-up context.
- **FR-010**: The system MUST display and allow management of signals, including signal text, confidence, and optional source context.
- **FR-011**: The system MUST display and allow management of opportunities, including status, description, follow-up date, and linked people.
- **FR-012**: The system MUST display and allow management of relationship links between people without hardcoding the relationship types.
- **FR-013**: The system MUST display open loops and follow-ups in both overview-level and person-level contexts.
- **FR-014**: Users MUST be able to create a new person record from the desktop app with name required and all other person fields optional.
- **FR-015**: Users MUST be able to edit existing person records from the desktop app.
- **FR-016**: The system MUST support multiline editing and display for long-form fields without truncating stored content.
- **FR-017**: The system MUST preserve existing local records and use the current backend/service layer as the source of truth.
- **FR-018**: The system MUST NOT introduce a second independent data model for the frontend.
- **FR-019**: The system MUST preserve the current local-first storage strategy and store portable app data inside the portable app folder when running in portable mode.
- **FR-020**: The system MUST provide clear empty, loading, validation, and error states for core views and forms.
- **FR-021**: The system MUST remain usable when the dossier contains more information than fits on screen by allowing scrolling within the app experience.
- **FR-022**: The system MUST NOT implement AI, semantic search, graph visualization, cloud sync, automation, voice interfaces, or external integrations as part of this feature.

### Key Entities *(include if feature involves data)*

- **Person**: The primary record in NetworkOps, representing an individual and their identity, relationship, strategic, and network-ops context.
- **Contact Method**: A way to reach a person, such as email, phone, LinkedIn, GitHub, social profile, or other contact value.
- **Interaction Log**: A recorded conversation or event involving one or more people, including summaries, takeaways, action items, sentiment, and follow-up context.
- **Signal**: A relationship intelligence observation about a person, including text, confidence, and optional source context.
- **Opportunity**: A possible future action or value path involving one or more people, including status, description, and follow-up date.
- **Relationship Link**: A connection between people or supported records that prepares NetworkOps for graph-style relationship context while remaining manually managed in this feature.
- **Open Loop/Follow-Up**: An action or pending item that helps the user remember what needs attention next.
- **Profile Photo**: A local image reference associated with a person and displayed in the dossier when available.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can launch the desktop app and open an existing person dossier in under 30 seconds from a normal local startup.
- **SC-002**: A user can create a new person with at least one contact method and one multiline dossier field in under 3 minutes.
- **SC-003**: A user can find and open a person from a local set of 100 person records in under 15 seconds.
- **SC-004**: 100% of saved multiline text entered through the GUI remains available after closing and reopening the app.
- **SC-005**: 100% of existing records created by the current local NetworkOps app remain visible through the desktop GUI.
- **SC-006**: A portable app folder can be copied and launched from another compatible Windows environment while preserving records created before copying.
- **SC-007**: The primary dossier view displays without overlapping text or controls at common desktop window sizes.
- **SC-008**: A user can add an interaction, signal, opportunity, and relationship link from the GUI and see each reflected in the relevant dossier section immediately after saving.

## Assumptions

- The desktop GUI is intended for a single local user.
- Windows is the first target platform for the executable experience.
- The existing backend/service layer remains the authoritative source for records and persistence.
- Existing local records should remain available without manual cleanup or re-entry.
- The GUI should prioritize the dossier-first visual experience from the mockup over recreating terminal workflows.
- The first GUI version may be desktop-focused and does not need mobile-specific layouts.
- The feature focuses on local app behavior, not cloud accounts, team sharing, or external service integrations.
