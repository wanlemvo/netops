# Architecture

## High-Level Flow

```text
User
  ↓
CLI executable / Python entry point
  ↓
Typer command layer
  ↓
Service layer
  ↓
Domain models and validation
  ↓
Repository layer
  ↓
SQLite database
```

## Main Modules

```text
src/netops/
├── cli.py              # Typer CLI commands
├── portable.py         # Portable executable entry point
├── domain/
│   ├── models.py       # Pydantic domain models
│   ├── suggestions.py  # Rule-based suggestion generation
│   └── validation.py   # Shared validation helpers
├── services/           # Use-case/service layer
├── storage/            # SQLite connection, migrations, repositories
└── tui/                # Legacy/experimental terminal UI
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

The portable executable sets `NETOPS_HOME` to its own folder.

## Schema Concepts

- `people`
- `person_contacts`
- `person_notes`
- `relationships`
- `interactions`
- `open_loops`
- `suggested_actions`
- `evaluations`

## Suggestion Flow

```text
People + interactions + open loops + evaluations
  ↓
Rule-based suggestion generator
  ↓
SuggestedAction records
  ↓
CLI output / dossier context
```

Suggestions are currently rule-based, not AI-generated.

