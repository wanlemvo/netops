# ADR 0007: Cross-Linking Strategy

## Status

Proposed

## Problem

Information should not exist in silos. Notes, signals, opportunities, and interactions may relate to multiple people or records.

For example, one meeting note may reference both Dr. Olav and Blair Reed. A single opportunity may involve one person as the owner, another as an introducer, and a note as supporting context. If NetworkOps stores these references only as plain text, the system cannot reliably show related context, backlinks, or future graph-style relationships.

## Decision

NetworkOps V1 will support explicit relationship tables rather than text-only references.

Initial linking should be manual. Users or app flows should create explicit links between records when context needs to be preserved. Future hyperlink-style experiences may be added later, but V1 should not depend on automatic link detection.

Initial relationships:

- person <-> note
- person <-> interaction
- person <-> signal
- person <-> opportunity
- person <-> person

These relationships should be represented through stable record IDs rather than display names or freeform text.

## Rationale

This follows knowledge-management and graph-based system patterns used by Obsidian and Wikipedia while remaining compatible with relational storage. Obsidian-style linking shows the value of connecting ideas explicitly. Wikipedia-style cross-referencing shows the value of navigable context. CRM-style relationships show the importance of maintaining structured links between people, accounts, activities, and opportunities.

Explicit relationship tables allow NetworkOps to preserve those patterns without requiring a graph database in V1.

## Consequences

- Related context can be found through links instead of text search alone.
- A note can eventually link to multiple people.
- An interaction can eventually include multiple participants.
- Person-to-person relationships can be modeled without overloading person fields.
- Backlinks and graph-style navigation become possible later.
- Manual linking creates some user effort in V1, but avoids unreliable automatic linking.

## Non-Goals

- This decision does not implement automatic link detection.
- This decision does not implement graph visualization.
- This decision does not implement semantic search.
- This decision does not add AI-generated links.
- This decision does not create database migrations yet.
