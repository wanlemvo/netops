# Desktop reconciliation provenance

The reference is the executable at `netops/netops/netops-gui/netops-gui.exe` inside the supplied ZIP.
Its SHA-256 is `7e1323746eef8c9f92492cedbbacee5ae6e74a847115316aefa9325414266328`.
The extracted reference executable has the same hash.

Inspection of its PyInstaller archive identified Python 3.12. All 26 embedded NetOps modules
and the launcher match compiled ZIP source after normalizing embedded source filenames.
The three bundled HTML/CSS/JavaScript assets match exactly. The extracted source matches
all 32 source/asset files in the ZIP. This establishes the source snapshot, not the original
build-machine directory or a reproducible clean commit.

The ZIP source branch was `005-desktop-gui-shell`, based on `16d2e27`, with additional
uncommitted and ignored GUI files. Its `netops/` ignore rule unintentionally ignored
`src/netops/` additions. The canonical repository is now [wanlemvo/netops](https://github.com/wanlemvo/netops).
Both repositories share `b2a6274`; a preservation commit and a two-parent reconciliation
merge retain the desktop and imported histories. Original files and Git metadata were
also captured in private ZIP snapshots before changes.

The user's confirmed launch path is `<portable-root>/netops-gui/netops-gui.exe`.
The embedded path logic selects `<portable-root>/data/netops.sqlite3`.
No NETOPS_DB or NETOPS_HOME process/user/machine override was found during inspection.
The database matches the ZIP copy and passed SQLite integrity checking. This conclusion
comes from verified code and launch location; the original installation was not launched
to observe an operating-system file handle.

Six distinct databases were backed up independently using SQLite's backup API, including
portable, source, preview, old portable, and home-directory variants. No records were merged.
Backups and personal paths are recorded in the private reconciliation manifest, never release assets.

## Material choices

- The later source contains the desktop GUI and expands the shared service/storage model;
  earlier dossier, raw-note, CLI and TUI support remains, with regression coverage.
- The separate CustomTkinter prototype has actions, exports and seeding concepts but a
  different schema and framework. Its imports expect directories absent from the supplied
  flat folder. Preserve its snapshot; do not merge its personal seeds or create a second GUI.
- Extend existing follow-up sources with completion timestamps rather than inventing a parallel
  task store. Completion does not erase interaction history or close business opportunities.
- Build in a fresh output directory without reading live data. Every release records its exact
  clean source commit and installed build dependencies.
