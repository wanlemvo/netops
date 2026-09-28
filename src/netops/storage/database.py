from __future__ import annotations

import os
import sqlite3
from pathlib import Path


class AtomicConnection(sqlite3.Connection):
    """Allow service transactions to contain repository transactions."""

    _depth = 0
    _failed = False

    def __enter__(self):
        if self._depth == 0:
            self.execute("BEGIN")
            self._failed = False
        self._depth += 1
        return self

    def __exit__(self, exc_type, exc, traceback):
        self._failed = self._failed or exc_type is not None
        self._depth -= 1
        if self._depth == 0:
            if self._failed:
                self.rollback()
            else:
                self.commit()
        return False


def default_database_path() -> Path:
    override = os.environ.get("NETOPS_DB")
    if override:
        return Path(override)

    app_home = os.environ.get("NETOPS_HOME")
    if app_home:
        return Path(app_home) / "data" / "netops.sqlite3"

    home = Path.home()
    return home / ".netops" / "netops.sqlite3"


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    db_path = Path(path) if path is not None else default_database_path()
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, factory=AtomicConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
