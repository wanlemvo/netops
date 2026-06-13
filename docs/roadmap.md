# Roadmap

## Near-Term Cleanup

- Keep CLI/executable workflow as the primary app surface.
- Decide whether to remove, archive, or fully separate the existing TUI code.
- Keep generated binaries and local databases out of git.
- Consolidate old Spec Kit artifacts or move them under documentation/archive.
- Add screenshots and demo assets under `assets/`.

## Product Improvements

- Continue refining structured contact methods, primary contact selection, and profile photo handling.
- Add edit flows for open-loop due dates, notes, and priority.
- Improve suggestion lifecycle and explainability.
- Add export/backup workflows for the SQLite database.
- Add safer restore/import behavior for portable use.

## Architecture Improvements

- Split CLI commands from workflow/use-case logic more cleanly.
- Keep domain models separate from persistence mapping.
- Reduce state-machine complexity if the TUI is retained.
- Continue expanding explicit relationship edges through `relationship_links`.
- Preserve the distinction between profile data and interaction/event history.

## Future Ideas

- Contextual AI summaries grounded in the local dossier.
- Relationship graph views or graph-like traversal.
- Evidence-backed suggestions.
- Semantic search over local relationship intelligence.
- Graph visualization.
- Automation and reminders.
- Solo module integration.
- External system integrations such as Obsidian, Notion, Gmail, or calendar tools.

These future ideas are intentionally outside the NetworkOps V1 implementation scope.
