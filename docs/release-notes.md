# NetOps 0.2.0 — desktop reconciliation candidate

- Reconcile the verified GUI source and earlier dossier work while retaining both Git histories.
- Repair dynamic dossier actions, add Edit Person, and separate record browsing from creation.
- Preserve drafts on errors, prevent duplicate submission and make person saves atomic.
- Include interaction follow-ups, support unscheduled follow-ups, completion and rescheduling.
- Add schema version 5 with completion timestamps and recovery of previously omitted dated follow-ups.
- Remove outer-folder naming dependency and report the selected database in the GUI.
- Correct operator identity and replace unsupported capability claims.
- Package assets, provide a clean data-free Windows build, and record source/dependency provenance.

This is a local review candidate, not a published release. Requires Windows 10/11 with Edge WebView2.
No project license has been selected; licensing remains a decision before public distribution.
Tags management, Analytics and Map View are not implemented. Photo management remains available
through the CLI; the GUI displays stored photos. No cloud sync or database encryption is provided.
