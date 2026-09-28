# Data locations, backups, and upgrades

Open **Data location** in the GUI to see the actual SQLite file selected by that running app.
`NETOPS_DB` overrides the database path; otherwise `NETOPS_HOME/data/netops.sqlite3` is used.
The portable launcher sets NETOPS_HOME from its marker or existing sibling data directory.
A normal source-installed GUI without overrides uses `~/.netops/netops.sqlite3`.

Keep the whole portable folder together, including `.netops-portable`, `data/`, and executable
subfolders. Renaming its outer folder is supported. If two possible databases are found, startup
stops and asks you to select NETOPS_HOME or NETOPS_DB; it does not pick or merge one silently.

Before upgrading, close all NetOps windows and terminal sessions. Copy the entire data folder
to a dated private backup. If another process may still be writing, use SQLite's backup API
for the database rather than copying only the main file; uncheckpointed changes may be in
`-wal`/journal files. Preserve photo assets as well. Verify the backup with `PRAGMA integrity_check`.

Extract a new release into a separate folder. Copy the backed-up data into that new folder,
then launch and verify people, history and follow-ups. Do not overwrite your only working copy.
The schema upgrades add columns and preserve legacy records. Test rollback by restoring the
entire old backup into the old installation; an older executable is not a migration downgrade tool.

The release builder never reads or copies personal data. Fictional demo creation is explicit and
refuses an existing destination. Backups and local databases are ignored by Git, but still need
normal access controls and your own off-device backup. SQLite contents are not encrypted.
