from __future__ import annotations

import os
import sys
from pathlib import Path


def portable_home() -> Path:
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        candidates = [executable_dir, executable_dir.parent]
        marked = [p for p in candidates if (p / ".netops-portable").is_file()]
        existing = [p for p in candidates if (p / "data" / "netops.sqlite3").is_file()]
        if len(existing) > 1 or len(marked) > 1 or (marked and existing and marked[0] != existing[0]):
            raise RuntimeError("Multiple portable data locations found. Set NETOPS_HOME or NETOPS_DB explicitly.")
        if marked:
            return marked[0]
        if existing:
            return existing[0]
        if executable_dir.name.lower() in {"netops-cli", "netops-gui"}:
            return executable_dir.parent
        return executable_dir
    return Path(__file__).resolve().parents[2]


def main(default_command: str = "gui") -> None:
    if "NETOPS_HOME" not in os.environ and "NETOPS_DB" not in os.environ:
        os.environ["NETOPS_HOME"] = str(portable_home())
    if len(sys.argv) == 1:
        sys.argv.append(default_command)

    from netops.cli import app

    app()


if __name__ == "__main__":
    main()
