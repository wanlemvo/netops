# ADR 0002: Separate Person Records from Event Records

## Status

Proposed

## Context

The Person Intelligence Record is the durable center of a relationship, but interaction logs, notes, signals, and opportunities grow over time. Flattening every event and observation into a person profile would make profiles noisy, harder to edit, and harder to connect later.

## Decision

Keep people separate from interaction logs, notes, signals, and opportunities. A person record should summarize durable relationship intelligence, while event-based and action-based records should live in their own tables.

## Consequences

- Person profiles remain readable and focused.
- Interaction history can grow without bloating the core person record.
- Notes can exist independently and do not need to belong to a single person.
- Signals and opportunities can accumulate as separate pieces of intelligence.
- Future cross-linking and backlinks become easier because records have their own identities.

## Non-Goals

- This decision does not implement new UI flows.
- This decision does not require notes or interactions to support multiple linked people in V1.
