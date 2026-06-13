# NetOps CLI

NetOps CLI is a portable, local-first relationship operations app. It stores people, contact methods, interactions, signals, opportunities, relationship links, follow-ups, suggestions, and evaluations in SQLite, with a Windows executable build that can travel with its `data/` folder.

## Status

This repository is being cleaned up around the executable CLI app as the main product surface. The command-line workflow is the durable interface; older terminal UI code still exists in `src/` while the project is being reorganized.

## Repository Layout

```text
netops-cli/
+-- README.md
+-- docs/
|   +-- project-overview.md
|   +-- architecture.md
|   +-- roadmap.md
|   +-- lessons-learned.md
|   +-- architecture/
|   +-- adr/
|   +-- schema_v1.md
+-- src/
+-- tests/
+-- assets/
|   +-- screenshots/
|   +-- demo/
+-- scripts/
+-- .gitignore
```

## Install For Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## CLI Usage

```powershell
netops --help
netops people add --name "Avery Chen" --organization "Northwind" --next-action "Send portfolio" --follow-up-date "2026-06-15"
netops people list
netops people contact add "Avery Chen" --type email --value "avery@example.com" --primary
netops log-v1 --person "Avery Chen" --type meeting --summary "Discussed migration" --action-items "Send notes"
netops signal add "Avery Chen" --text "Responds well to direct follow-through" --confidence high
netops opportunity add --person "Avery Chen" --title "Portfolio Review" --follow-up-date "2026-06-15"
netops loops review-v1
```

## Portable Build

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-portable.ps1
```

The portable output is:

```text
portable/netops-cli/
+-- netops.exe
+-- data/
    +-- netops.sqlite3
    +-- assets/
        +-- profile_photos/
```

Copy the whole `portable/netops-cli/` folder to move the app and its data together.

## Documentation

- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [NetworkOps V1 Architecture](docs/architecture/networkops_v1_architecture.md)
- [Schema V1](docs/schema_v1.md)
- [Roadmap](docs/roadmap.md)
- [Lessons Learned](docs/lessons-learned.md)
