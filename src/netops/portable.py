from __future__ import annotations

import os
import sys
from pathlib import Path


def portable_home() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def main() -> None:
    os.environ.setdefault("NETOPS_HOME", str(portable_home()))
    (Path(os.environ["NETOPS_HOME"]) / "data" / "assets" / "profile_photos").mkdir(parents=True, exist_ok=True)
    if len(sys.argv) == 1:
        sys.argv.append("tui")

    from netops.cli import app

    app()


if __name__ == "__main__":
    main()
