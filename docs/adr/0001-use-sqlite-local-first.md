# ADR 0001: Use SQLite for Local-First Storage

## Status

Proposed

## Context

NetworkOps V1 is currently a CLI app that needs to store structured person intelligence records, contact methods, interaction logs, notes, signals, opportunities, tags, and relationship links. The app should remain portable and local-first, with data persisting inside the app folder or data folder.

## Decision

Use SQLite as the primary local storage engine for NetworkOps V1 structured data.

## Consequences

- The app can run without a server, cloud account, or network connection.
- Data can be stored in a portable `data/netops.db` file.
- Relational structures such as people, contact methods, logs, signals, opportunities, and links can be represented cleanly.
- Migrations can evolve the schema over time while preserving existing local data.
- Future sync or server-backed storage would require an explicit migration or adapter decision.

## Non-Goals

- This decision does not implement cloud sync.
- This decision does not add AI, semantic search, or graph visualization.
