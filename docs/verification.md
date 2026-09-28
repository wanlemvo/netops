# Verification — 28 September 2026

| Check | Executed result |
|---|---|
| Clean checkout + installed wheel | **111 tests passed**, including the real browser workflow; no source-tree import shortcut (`-o pythonpath=`) |
| Package artifacts | Wheel and source distribution built; installed GUI assets and entry point verified in a separate environment |
| Browser workflow | Create from filtered search; edit; validation and network failure preserve draft; log/complete follow-up; add contact/signal/opportunity/link; reload; distinguish duplicate names; 1024/1440 px layouts |
| Backend/storage | Atomic failed writes, migration rollback, follow-up completion/rescheduling, legacy compatibility, existing CLI/TUI regression tests |
| Database backups | Six independent SQLite snapshots restored and migrated; integrity and foreign keys passed; original row identities and all nonempty fields retained |
| Native Windows executable | A visible pywebview window exposed rendered Dashboard and Add Person controls through Windows UI Automation; native-window screenshot inspected |
| Portable move/restart | Copied executable launched before and after renaming its folder with spaces; reported database path followed the folder and the saved fictional record persisted |
| Release archive | Both executables, portable marker, README and build manifest; all manifest hashes verified; **zero databases** |
| Repository audit | No tracked or historical database/executable/archive files and no matches for the recognized credential/private-key patterns across local refs |
| Original installation | Reference executable and active database hashes remain unchanged |

The tested application binaries were built from clean commit
`fbb89e2c5100cccbcfc9198b1c493d896110a004`. Subsequent commits add the verification harness,
evidence and a release filename correction; they do not change the application code in those binaries.
The candidate archive is `dist/netops-0.2.0-fbb89e2c.zip`; its adjacent SHA-256 file and embedded
`netops/build-manifest.json` identify the artifacts and dependencies.

The native smoke check verifies actual WebView2 rendering, launch, shutdown, database selection
and persistence through the packaged HTTP API. Complete click/form workflows were exercised in
Microsoft Edge against the same GUI/backend. These are distinct checks; no claim is made that
the whole browser click sequence was repeated through Windows UI Automation.

The restricted execution session could open a native frame but could not establish rendered
WebView2 controls. The successful native checks ran in the regular Windows desktop session;
both final launch logs were empty. Earlier diagnostic failures are retained in ignored artifacts.
PyInstaller emitted optional-platform/module warnings (Android, parser tables and tzdata);
the built Windows candidate passed the checks above. CI configuration was added but has not
run on GitHub because nothing has been pushed.

Local evidence: `artifacts/clean-tests.xml`, `artifacts/native-desktop-check3/results.json`,
`artifacts/restore-results.json`, `artifacts/data-preservation-results.json`,
`artifacts/repository-audit.json`, and package/build logs. Private backups live under
`.reconciliation/20260928/`, including source/Git snapshots and a database manifest.
The token-pattern audit is a bounded scan, not a guarantee that all sensitive prose is absent;
historical examples still warrant a publication review.

To repeat native verification with isolated data:

```powershell
.venv/Scripts/python scripts/verify_windows.py --exe dist/netops-0.2.0-fbb89e2c/netops/netops-gui/netops-gui.exe --output artifacts/new-native-check
```

The output directory must not exist. The script copies the binary, seeds fictional data, checks
rendered controls, saves a record, closes the window, renames the copy and checks it again.
