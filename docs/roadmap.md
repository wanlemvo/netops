# Roadmap

## Near-Term Cleanup

- Keep CLI/executable workflow as the primary app surface.
- Decide whether to remove, archive, or fully separate the existing TUI code.
- Keep generated binaries and local databases out of git.
- Consolidate old Spec Kit artifacts or move them under documentation/archive.
- Add screenshots and demo assets under `assets/`.

## Product Improvements

- Improve contact management beyond add/delete.
- Add edit flows for open-loop due dates, notes, and priority.
- Improve suggestion lifecycle and explainability.
- Link raw notes to people, interactions, contacts, open loops, and suggestions.
- Add export/backup workflows for the SQLite database.
- Add safer restore/import behavior for portable use.

## Architecture Improvements

- Split CLI commands from workflow/use-case logic more cleanly.
- Keep domain models separate from persistence mapping.
- Reduce state-machine complexity if the TUI is retained.
- Make relationship edges more explicit.
- Preserve the distinction between profile data and interaction/event history.

## Future Ideas

- Contextual AI summaries grounded in the local dossier.
- Relationship graph views or graph-like traversal.
- Evidence-backed suggestions.
- Automatic promotion of raw notes into structured fields.

