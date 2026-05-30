# NetOps CLI

NetOps CLI is a portable, local-first relationship operations app. It stores structured people dossiers, contact methods, interactions, notes, follow-ups, suggestions, and evaluations in SQLite, with a Windows executable build that can travel with its `data/` folder.

## Status

This repository is being cleaned up around the executable CLI app as the main product surface. The command-line workflow is the durable interface; older terminal UI code still exists in `src/` while the project is being reorganized.

## Repository Layout

```text
netops-cli/
├── README.md
├── docs/
│   ├── project-overview.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── lessons-learned.md
├── src/
├── tests/
├── assets/
│   ├── screenshots/
│   └── demo/
├── scripts/
└── .gitignore
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
netops people add --name "Avery Chen" --organization "Northwind"
netops people list
netops log "Avery Chen" --type meeting --notes "Discussed migration" --follow-up "Send notes"
netops loops list
netops suggest
```

## Portable Build

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-portable.ps1
```

The portable output is:

```text
portable/netops-cli/
├── netops.exe
└── data/
    └── netops.sqlite3
```

Copy the whole `portable/netops-cli/` folder to move the app and its data together.

## Documentation

- [Project Overview](docs/project-overview.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Lessons Learned](docs/lessons-learned.md)

