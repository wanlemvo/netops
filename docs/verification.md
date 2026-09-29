# Verification — 28 September 2026

## Current case-file iteration

The implementation is documented in [casefile-iteration.md](casefile-iteration.md).
The final Windows candidate was built from clean commit
`9447015806d571a66dd09506bd1d0f458deb5b52` on `codex/reconcile-desktop`.

| Check | Executed result |
|---|---|
| Full installed-package suite | **122 passed** from a clean export of `2b963095`; isolated installed wheel, no source-tree import shortcut |
| Final layout / package | Only four CSS lines changed after that full run; final `94470158` wheel rebuilt from a clean export, all three GUI assets verified byte-for-byte, both browser workflows passed again |
| Backend / migrations | Section revision conflicts and source preservation; tag union and reusable type normalization; unknown dates; Intel provenance; simultaneous Coworker + Friend, ending one, restarting with a new ID; derived chronology; completion cycles |
| Browser | Standalone directory; collapse without reload or draft loss; failed saves; duplicate names; section Edit/Append/History; photo preview/save; tags; multiple participants; Intel correction/history; relationship ending/re-adding; reload; 1024/1440 layouts |
| SQLite restoration | Consistent backup of a genuine v4 fictional fixture restored and migrated to schema 10; original text/IDs preserved and foreign keys checked |
| Native Windows | Final packaged pywebview window rendered Dashboard, People and Intel controls; Windows UI Automation and native screenshots verified |
| Portable move / restart | Copied final executable launched, saved a fictional record and photo, closed, moved to a renamed folder with spaces, reopened and retrieved both record and JPEG photo |
| Release ZIP | Manifest file hashes and ZIP SHA-256 verified; **zero databases** in the archive |
| Personal installation | Development, package, browser and native checks used isolated fictional data; the flash-drive installation and personal database were not upgraded |

Final archive: `dist/netops-0.2.0-94470158.zip`.
SHA-256: `50ec31958ed9fe033d2ab4bd74d4413d01fd8f75551888c6c86b9063c3b0372e`.
The embedded build manifest records Python 3.12.14, dependency versions, build settings and binary hashes.
Wheel and source distribution: `artifacts/casefile-release-package/packages/`.
The fictional preview launcher is `artifacts/NetOps Casefile Preview/Open NetOps Preview.cmd`;
it explicitly selects its own database, regardless of existing environment overrides.

Native launch, rendering and persistence checks are distinct from browser click/form tests. The entire
browser sequence was not repeated through Windows UI Automation. Updated screenshots and the recorded
browser workflow are in [demo](demo/README.md).

Evidence: `artifacts/casefile-package-final/tests.xml`, `artifacts/casefile-release-package/browser-tests.xml`,
`artifacts/casefile-native-final/results.json`, `artifacts/casefile-release-results.json`, and adjacent logs.
An initial package test attempt could not access Windows' shared pytest temp folder; rerunning with an
explicit new isolated test directory resolved it. PyInstaller reported optional platform/module warnings;
the resulting Windows executable passed the native checks. GitHub CI has not run because nothing was pushed.

Later documentation/capture commits do not change application code or the candidate's provenance.
Older local candidates remain retained; the archive named above is the final candidate for this iteration.

## Original reconciliation evidence (earlier build)

The results below describe the earlier executable, not the current case-file candidate.

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
