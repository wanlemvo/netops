# ADR 0005: Design for Future Relationship Graph

## Status

Proposed

## Context

NetworkOps V1 should not implement graph visualization or a full knowledge graph, but the product direction points toward cross-linking people, notes, signals, opportunities, and interactions. Designing only for one-way contact records would make that future harder.

## Decision

Include a relationship-link concept that can connect one entity to another and prepare for future graph-style relationships, backlinks, and cross-linking.

## Consequences

- V1 can stay simple while leaving room for richer relationship intelligence later.
- Notes may eventually link to multiple people.
- Interaction logs may eventually involve multiple participants.
- Signals and opportunities can later reference their sources and related records more explicitly.
- The system can grow toward graph-like navigation without replacing the core V1 tables.

## Non-Goals

- This decision does not implement graph visualization.
- This decision does not implement semantic search.
- This decision does not require AI-generated links.
