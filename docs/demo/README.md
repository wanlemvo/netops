# Fictional demo

All names, organizations, interactions and contact details in these captures are fictional.
The screenshots show the running application, not mockups. The recording is an automated browser
workflow against the same GUI assets and backend; it is not a recording of the native window.

Create a separate dataset from the repository root:

```powershell
.venv/Scripts/python -m netops.demo --database artifacts/demo/netops.sqlite3
$env:NETOPS_DB = (Resolve-Path artifacts/demo/netops.sqlite3).Path
.venv/Scripts/netops-gui.exe
```

For repeatable screenshots and a workflow recording:

```powershell
.venv/Scripts/python -m playwright install ffmpeg
$env:NETOPS_BROWSER_TESTS = '1'
$env:NETOPS_CAPTURE_DIR = 'docs/demo'
.venv/Scripts/python -m pytest tests/integration/test_gui_browser.py -q
```

On Linux, install Playwright Chromium instead. Tests create fresh temporary databases.
Capture script: inspect Dashboard → Avery dossier → search for a missing person → add Rowan Quinn
→ edit multiline dossier → demonstrate invalid-date feedback → save → log and complete a follow-up
→ add contact, signal, opportunity and relationship → reload and verify persistence.

![Dashboard](dashboard.png)

![Dossier](dossier.png)
