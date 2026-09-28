from __future__ import annotations

from prompt_toolkit.styles import Style


CYBERPUNK_STYLE = Style.from_dict(
    {
        "title": "bold #00ffd5",
        "subtitle": "#ff2bd6",
        "border": "#00aaff",
        "selected": "reverse bold #00ffd5",
        "disabled": "#666666",
        "hint": "#9dff00",
        "error": "bold #ff3b3b",
        "status": "#00aaff",
        "field": "#ffffff",
        "field_active": "reverse #ffffff",
        "logo": "bold #9dff00",
        "logo_accent": "bold #ff2bd6",
    }
)

HEADER = r"""
 _   _  _____  _____  ____  ____  ____
| \ | || ____||_   _|/ __ \|  _ \/ ___|
|  \| ||  _|    | | | |  | | |_) \___ \
| |\  || |___   | | | |__| |  __/ ___) |
|_| \_||_____|  |_|  \____/|_|   |____/
"""
FOOTER = "UP/DOWN move  ENTER select  ESC back"
