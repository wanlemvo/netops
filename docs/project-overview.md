# Project Overview

NetOps CLI is a local-first relationship operations system. It is designed to help a user remember people, preserve interaction context, track follow-ups, and generate simple next-action suggestions without relying on a cloud service.

The project started as a relationship tracking CLI and expanded into structured person dossiers. A dossier combines profile data, contact methods, relationship notes, personal intelligence, interaction history, open loops, suggestions, evaluations, and raw notes.

## What Exists Today

- Python package under `src/netops`
- Typer/Rich CLI commands
- SQLite persistence
- Pydantic domain models
- Repository/service layers
- Prompt-toolkit terminal UI code
- Portable Windows executable build script
- Tests across unit, integration, and contract layers

## Product Direction

The project is being oriented around the executable CLI app as the primary product surface. The goal is a clean portable tool that can be run from a folder, use a local SQLite database, and avoid cloud dependencies.

The TUI code still exists, but the repo structure and docs now emphasize the CLI/executable app first.

