# Current case-file iteration — 28 September 2026

The canonical source remains `codex/reconcile-desktop`. This iteration changes the GUI and shared
domain layer in place. The installed flash-drive executable and personal database have not been
replaced or upgraded during this work. A new release candidate must be identified by its build manifest.

## Implemented phases

1. Persistent application bar, collapsible navigation, standalone People directory, full profile,
   shared global/contextual creation, Intel naming, functional Tags destination, and disabled Network Map.
2. Identity, relationship context, current context, knowledge, open loops, and recent history sections.
   Imported Markdown reads as formatted content. Individual case-file sections have Edit, Append,
   Add and History controls. Photos can be selected, previewed, replaced and removed.
3. Persistent interaction and relationship vocabularies, custom reusable types, normalized tag
   assignments, tag usage counts, searchable tag checkboxes, and inline tag creation in Edit Person.
4. Searchable multi-person interaction participants, explicit profile preselection, empty global
   selection, local event-date defaults, takeaways and action items. Missing/invalid historical event
   dates never become today. Original malformed values remain stored for future correction.
5. Fact / Observation / Signal / Inference / Unknown Intel with event date, source date, source,
   confidence, optional related interaction, origin, creator and creation timestamp. Corrections
   retain prior content/provenance. Existing Signals keep IDs and unknown metadata stays unknown.
6. Independently dated relationship-type episodes. Coworker and Friend coexist; ending Friend does
   not end Coworker; later Friend episodes get new IDs. Month precision is supported. Direction remains
   explicit. Corrections retain history; ended episodes cannot silently become a new active episode.
7. Derived Timeline includes interactions, relationship starts/ends, Intel and corrections, and
   follow-up completions. Repeated completion creates no duplicate event; rescheduling retains earlier
   completion history. Opportunities remain within profiles with existing data and follow-up behavior.

## Contracts and boundaries

| Area | Implementation |
|---|---|
| Frontend | `src/netops/gui/static/index.html`, `app.js`, `styles.css` |
| HTTP / desktop | `src/netops/gui/server.py`, pywebview / WebView2 |
| Application facade | `src/netops/services/app_backend.py` |
| Sections / photos | `services/casefile.py`, `storage/casefile.py` |
| Intel / relationship history | `services/intelligence.py`, `services/relationships.py` |
| Chronology | `services/timeline.py`, completion triggers in migration 10 |
| Vocabulary / tags | `storage/catalog.py`; existing `tags` and `taggings` retained |
| SQLite | `storage/repositories.py`, `storage/database.py`, additive migrations 6–10 |

Histories are limited to dossier sections, Intel corrections, relationship episode corrections and
follow-up completion events. They are not a general audit trail. Profile context edits update current
state. Imported prose remains source material, not inferred historical events. Original dossier text
is retained separately from section overrides. An intentional section Edit saves ordinary plain text;
the previous formatted version remains in History. Append retains existing formatting.

Equivalent historical tag rows are grouped as a single application choice without deleting original
tag IDs. Normalized taggings are authoritative for the GUI; compatibility JSON is synchronized on
application writes. Direct database modifications are outside that synchronization contract.

The interface is a local single-user tool. No AI, web research, server deployment, cloud sync,
encryption, graph infrastructure or Analytics module was added. Network Map remains disabled.
Tag rename/archive/merge and a rich-text authoring toolbar are not implemented. CLI/TUI feature
parity is not promised; original full-dossier editing through old administrative tools should be
avoided after creating section overrides. Use the GUI section controls for current case-file edits.

## Validation and release

See `docs/verification.md` for final executed results and release identity. Tests use isolated
fictional databases, including old-schema fixtures and consistent SQLite backup/restore. No tests
or builds use the personal database. Browser workflows and native Windows launch checks are reported
separately. Review the candidate in a separate folder before any personal-data upgrade.

No push, merge, publication, shared-history rewrite or flash-drive replacement is part of this pass.
Licensing and publication remain user decisions.
