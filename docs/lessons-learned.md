# Lessons Learned v0

## Purpose

This document preserves the product and architecture insights that emerged while shaping NetworkOps / NetOps CLI. These lessons matter because the project is not just a CRUD contact tracker. It is becoming a local-first relationship intelligence system, and the early implementation surfaced design boundaries that should guide the next version.

## Core Lessons

### Profiles and Interaction Logs Should Be Separate

A person profile is relatively stable. It holds identity, role, contact methods, relationship context, preferences, and long-lived personal intelligence.

An interaction log is event-based. It records what happened, when it happened, what was discussed, what commitments emerged, and what changed because of the interaction.

Mixing these two concepts makes the dossier harder to reason about. Profile fields should answer "who is this person and what do I know about them?" Interaction logs should answer "what happened with this person over time?"

### Notes Need Contextual Linking

Raw notes are useful, but unlinked notes become a pile. A note should eventually be able to connect to a person, interaction, contact method, open loop, suggestion, event, or relationship.

The current append-only note model is a useful start, but the real value comes when notes can answer:

- Why did I write this down?
- Who or what does it relate to?
- Did it create a follow-up?
- Did it change the profile?
- Is it evidence for a suggestion?

### AI Value Comes From Contextual Continuity

The valuable AI layer is not just generating generic follow-up ideas. The value comes from continuity: remembering context across people, interactions, commitments, and time.

Good suggestions should be grounded in:

- prior conversations
- open loops
- relationship strength
- recent outcomes
- important dates
- communication preferences
- unresolved notes
- patterns across the network

Without contextual continuity, AI becomes a thin reminder system. With it, the system becomes relationship intelligence.

### NetworkOps Is Not a Contact Manager

The project should not compete with a phone contacts app or CRM. It is not primarily about storing names, emails, and phone numbers.

NetworkOps is about operationalizing relationships:

- What do I know?
- What changed recently?
- What should I do next?
- What commitments are open?
- Who is connected to whom?
- What context should I remember before reaching out?

Contacts are only one layer. The deeper product is a memory and action system for a personal/professional network.

### The System Requires Graph-Like Relationships

Flat person records are not enough. The product naturally wants a graph:

- people connected to people
- people connected to organizations
- people connected to opportunities
- notes connected to interactions
- interactions connected to open loops
- suggestions connected to evidence
- outcomes connected back to prior actions

This does not necessarily require a graph database immediately, but the domain model should not pretend everything is flat. Future architecture should preserve relationship edges explicitly.

### Architecture Matters Earlier Than Expected

The first implementation moved quickly, but the TUI state machine became complex faster than expected. Forms, navigation, delete confirmations, dossier rendering, and workflow logic started gathering in one place.

That is a signal that architecture matters early for this project. The system needs clearer boundaries between:

- domain models
- storage repositories
- services/use cases
- TUI screen rendering
- TUI navigation state
- workflow actions
- AI/context generation

If these boundaries are not protected, the app will become difficult to extend exactly when the product starts getting interesting.

## Product Direction Lessons

### The Dossier Is the Primary Surface

The person dossier is the center of the app. It should feel like a structured intelligence page, not just a detail view.

The dossier should eventually answer:

- Who is this person?
- How do I reach them?
- What is our relationship?
- What have we talked about?
- What do I owe them?
- What might be useful to do next?
- What context should I remember?

### Command-Free Operation Matters

CLI commands are useful for power users, but the normal experience should not require remembering flags like `--follow-up` or `--due`.

The portable exe should open into a guided TUI where the user can navigate, add, edit, delete, and review without memorizing commands.

### Deletion Requires Deliberate Confirmation

Because the app stores personal relationship memory, destructive actions need clear confirmation. Delete flows should be explicit and reversible only through backups, not accidental keypresses.

The confirmation pattern should remain consistent for:

- people
- contact methods
- raw notes
- open loops
- suggestions
- future relationship edges

### Portable Data Is Part of the Product

The portable folder is not just a build artifact. It is part of the product experience.

The app should preserve this contract:

```text
netops-cli/
  netops.exe
  data/
    netops.sqlite3
```

If the folder moves to a USB drive or another computer, the data should move with it.

## Architecture Notes

### Contacts Need a Dedicated Model

Email and phone fields on `Person` are not enough. Contact methods need their own structure so a person can have multiple emails, numbers, social handles, websites, and labels.

The `person_contacts` table is a move in the right direction.

### Suggestions Need a Cleaner Lifecycle

Suggestions currently emerge from rules and are persisted for status tracking. That is useful, but the lifecycle needs refinement.

Future questions:

- When should a suggestion be regenerated?
- When should it be dismissed permanently?
- What evidence produced it?
- Should completing an open loop automatically complete related suggestions?
- Should suggestions be grouped by person, urgency, or opportunity?

### Raw Notes Are Not Enough Without Promotion

Raw notes should remain easy to capture, but important notes should be promotable into structured fields, contact methods, interactions, or open loops.

The ideal workflow is:

1. Capture rough note.
2. Link it to context.
3. Extract useful structure.
4. Preserve the original note as source evidence.

### Open Loops Are Commitments

Open loops are not just tasks. In this domain they represent commitments, promises, opportunities, or unresolved relationship threads.

That means they should remain attached to people and interactions, and eventually to relationship/opportunity context.

## Risks To Watch

- The TUI state machine can become too large.
- The dossier can become visually noisy if every field is shown without hierarchy.
- Notes can become unmanageable without linking and promotion.
- Suggestions can become annoying if they are not grounded in context.
- The app can drift into being a generic CRM if relationship intelligence is not kept central.
- Portable builds can become confusing if source folder, build folder, and data folder are not clearly distinguished.

## Next-Version Principles

- Keep profile data separate from event history.
- Treat relationships as edges, not just text fields.
- Make all normal workflows available through the TUI.
- Preserve raw evidence before deriving structure.
- Make AI/context features explainable.
- Keep the portable data contract simple.
- Refactor TUI architecture before adding many more screens.
- Design for continuity over time, not just storage.

