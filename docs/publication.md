# Public repository and distribution

The canonical repository is [wanlemvo/netops](https://github.com/wanlemvo/netops), with the desktop GUI
on `main`. The former repository URL redirects here. Existing commit history is retained.

## Visible on GitHub

- README with an actual dossier screenshot, working features, demo download and workflow recording.
- Python services/storage, HTML/CSS/JavaScript GUI, tests, packaging scripts, dependency pins and CI.
- Fictional demo seed (`src/netops/demo.py`), application screenshots and a browser workflow recording.
- Architecture, feature inventory, verification, backup/restore, release notes, roadmap and historical documents.
- Commit authorship, previous commits and archive tags. Archiving does not hide public history.

Private application databases, imported dossiers, photo assets, source snapshots, local test artifacts
and reconciliation backups are excluded from Git and release inputs. The current test fixtures use
fictional examples. Historical commits retain their original examples, including names that previously
appeared in the public prototype repository; those commits have not been rewritten.

## Windows downloads

Both archives contain the same GUI and CLI executables, a portable marker, launcher, README and build
manifest. The non-demo archive contains no database. The `-demo` archive contains only a freshly generated
fictional database from the versioned seed. Its launcher selects its own database even if environment
overrides exist. Nothing imports a personal workspace or merges databases automatically.

Each manifest identifies the exact clean source commit, Python/dependency versions, build settings and
file hashes. Adjacent SHA-256 files verify the archives. Seeded database hashes apply before first launch;
normal use changes the database. The repository is source and documentation, not a hosted application.

## Archive policy

The previous `main`, `003-dynamic-person-dossier` and `004-person-intelligence-record` branch tips are
retained under `archive/2026-10-03/…` tags before retiring obsolete remote branches. The prototype release
tag remains. The GUI reconciliation branch is merged with its history intact; `main` is the current entry
point. Private local Git bundles and installation backups provide additional recovery copies.

No project license has been selected. A license choice and review of bundled dependency notices remain
owner decisions; public visibility alone does not supply an open-source license for NetOps.
