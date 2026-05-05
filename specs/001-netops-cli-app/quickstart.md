# Quickstart: NetOps CLI App

This quickstart describes the planned developer and user validation flow for the feature.

## Prerequisites

- Python 3.11 or newer
- A terminal on Windows, macOS, or Linux
- Project dependencies installed in a virtual environment

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

For macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## First Run

```bash
netops --help
netops tui
```

Expected result: help output is available, and the TUI opens to the overview dashboard with empty-state guidance.

## Basic Workflow

```bash
netops people add --name "Avery Chen" --organization "Northwind" --tag mentor
netops relationship add "Avery Chen" --type mentor --notes "Quarterly career conversations"
netops log "Avery Chen" --type meeting --notes "Discussed platform migration and promised to send notes" --follow-up "Send migration notes" --due 2026-05-12
netops suggest
netops evaluate --person "Avery Chen" --outcome positive --notes "Follow-up strengthened trust"
```

Expected result: the person, relationship, interaction, open loop, suggestion, and evaluation are persisted locally and visible from the TUI dossier.

## TUI Smoke Flow

1. Launch `netops tui`.
2. Open People and confirm Avery Chen appears.
3. Open the dossier and confirm relationship notes, interaction history, and open loop.
4. Open Suggestions and confirm a follow-up suggestion includes a reason.
5. Open Evaluation and save an outcome for a completed action.

## Test Commands

```bash
pytest tests/unit
pytest tests/integration
pytest tests/contract
```

Expected result: unit tests validate domain rules, integration tests validate persistence and shared CLI/TUI behavior, and contract tests validate command and screen expectations.

## Validation Notes

- 2026-05-05: `python -m pytest` passed with 25 tests.
- Direct source invocation before editable install requires `PYTHONPATH=src` or the editable install step above.
