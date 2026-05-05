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
    }
)

HEADER = "NETOPS // RELATIONSHIP OPS TERMINAL"
FOOTER = "UP/DOWN move  ENTER select  ESC back"

