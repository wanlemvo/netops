# NetworkOps

NetworkOps is a portable, local-first relationship intelligence app. It stores people, contact methods, interactions, signals, opportunities, relationship links, follow-ups, suggestions, and evaluations in SQLite, with a Windows executable build that can travel with its `data/` folder.

## Status

This repository is evolving from a terminal-first prototype into a portable desktop GUI. The executable now launches the local GUI shell by default, while the CLI and interactive terminal menu remain available for power-user workflows and fallback operations.

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

## GUI Usage

For development:

```powershell
netops gui
```

For the portable build, double-click:

```text
netops/netops-gui/netops-gui.exe
```

The executable opens NetworkOps in its own desktop window. Data remains in the root `netops/data/` folder.

## CLI Usage

```powershell
netops --help
netops tui
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
netops/
+-- README.txt
+-- data/
+   +-- netops.sqlite3
+   +-- assets/
+       +-- profile_photos/
+-- netops-cli/
+   +-- netops-cli.exe
+   +-- README.txt
+-- netops-gui/
    +-- netops-gui.exe
    +-- README.txt
```

Copy the whole `netops/` folder to move both apps and their shared data together.

## Documentation

- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [NetworkOps V1 Architecture](docs/architecture/networkops_v1_architecture.md)
- [Schema V1](docs/schema_v1.md)
- [Roadmap](docs/roadmap.md)
- [Lessons Learned](docs/lessons-learned.md)
