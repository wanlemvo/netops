# Portable Windows Build

This project can run with all app data inside one folder.

## Folder Layout

After building, the copyable folder looks like this:

```text
docs/modules/
└── network_ops/

```

`netops.exe` sets `NETOPS_HOME` to its own folder. The default database path then becomes:

```text
portable/netops-cli/data/netops.sqlite3
```

Double-clicking `netops.exe` launches the TUI. Running it from PowerShell also supports the normal CLI commands:

```powershell
.\portable\netops-cli\netops.exe people list
.\portable\netops-cli\netops.exe suggest
.\portable\netops-cli\netops.exe tui
```

## Build

From the repo root:

```powershell
.\scripts\build-portable.ps1
```

If `python` is not on PATH, pass the full path:

```powershell
.\scripts\build-portable.ps1 -Python "C:\Path\To\python.exe"
```

If a previous build left an incomplete `.venv`, recreate it:

```powershell
.\scripts\build-portable.ps1 -RecreateVenv
```

## Move Existing Data

If you already have app data from the old default location, copy:

```text
C:\Users\<old-user>\.netops\netops.sqlite3
```

to:

```text
portable\netops-cli\data\netops.sqlite3
```
