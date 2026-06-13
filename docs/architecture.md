# Architecture

## High-Level Flow

```text
User
  |
CLI executable / Python entry point
  |
Typer command layer
  |
Service layer
  |
Domain models and validation
  |
Repository layer
  |
SQLite database
```

## Main Modules

```text
src/netops/
+-- cli.py              # Typer CLI commands
+-- portable.py         # Portable executable entry point
+-- domain/
|   +-- models.py       # Pydantic domain models
|   +-- suggestions.py  # Rule-based suggestion generation
|   +-- validation.py   # Shared validation helpers
+-- services/           # Use-case/service layer
+-- storage/            # SQLite connection, migrations, repositories
+-- tui/                # Interactive terminal UI
```

## Persistence

SQLite is the local datastore. The default database path is:

```text
%USERPROFILE%/.netops/netops.sqlite3
```

When `NETOPS_HOME` is set, the app uses portable storage:

```text
NETOPS_HOME/data/netops.sqlite3
```

The portable executable sets `NETOPS_HOME` to its own folder. Profile photo assets copied by the app live under:

```text
NETOPS_HOME/data/assets/profile_photos/
```

## Schema Concepts

NetworkOps V1 uses `docs/schema_v1.md` as the canonical schema design and `docs/architecture/networkops_v1_architecture.md` as the technical architecture reference.

Core V1 records:

- `people`
- `contact_methods`
- `interactions`
- `interaction_people`
- `signals`
- `opportunities`
- `opportunity_people`
- `relationship_links`
- `tags`
- `taggings`

Legacy compatibility records still exist for existing data and older flows, including open loops, suggestions, evaluations, and legacy raw notes. Standalone notes are not a V1 entity.

## Suggestion Flow

```text
People + interactions + open loops + evaluations
  |
Rule-based suggestion generator
  |
SuggestedAction records
  |
CLI output / dossier context
```

Suggestions are currently rule-based, not AI-generated. V1 opportunities are visible follow-up records; they are not treated as AI recommendations.
