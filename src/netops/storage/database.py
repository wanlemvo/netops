from __future__ import annotations

import os
import sqlite3
from pathlib import Path


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
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
