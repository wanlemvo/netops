# NetOps project instructions

The desktop GUI is the primary product. Preserve its visual direction and shared Python services.
Use src/netops/gui, SQLite storage, and pywebview; do not introduce another application framework.
Run tests with `.venv/Scripts/python -m pytest`. Use isolated fictional databases.
Never run builds or tests against personal data. Releases must contain no personal database.
Historical specifications describe earlier CLI/TUI iterations and are not current product direction.
See README.md and docs/architecture.md for current behavior and commands.
