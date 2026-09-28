from __future__ import annotations

import os
import sys
from pathlib import Path


def portable_home() -> Path:
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        if executable_dir.name in {"netops-cli", "netops-gui"} and executable_dir.parent.name.lower() == "netops":
            return executable_dir.parent
        return executable_dir
    return Path(__file__).resolve().parents[2]


def main(default_command: str = "gui") -> None:
    os.environ.setdefault("NETOPS_HOME", str(portable_home()))
    (Path(os.environ["NETOPS_HOME"]) / "data" / "assets" / "profile_photos").mkdir(parents=True, exist_ok=True)
    if len(sys.argv) == 1:
        sys.argv.append(default_command)

    from netops.cli import app

    app()


if __name__ == "__main__":
    main()
