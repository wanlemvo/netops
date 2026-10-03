# Verification

## Publication checks

The publication preparation suite passed **123 tests with zero failures or skips**, including both
browser workflows and the fictional demo packaging regression. Tests use isolated fictional databases.
The demo packaging check verifies exactly two fictional people, SQLite integrity, manifest hashes,
its explicit database launcher, and rejection of an input distribution containing a database.

The publication Windows build is from clean commit `35b836c9d10a6ea2fdb2e47f691b4be89a8801eb`.
On 3 October 2026, its native WebView2 controls rendered successfully and a copied distribution retained
its fictional record and JPEG photo after moving to a renamed folder containing spaces. Both archive
manifests/checksums were verified: zero databases in the empty edition, exactly one freshly seeded
fictional database in the demo. A clean-export wheel/source distribution built successfully; all GUI
assets matched source exactly. GitHub push and pull-request checks passed for that source commit.

GitHub runs backend, migrations, browser and package-install checks on pushes and pull requests.
[Live CI results](https://github.com/wanlemvo/netops/actions/workflows/checks.yml) show the exact tested
commit and result. Native Windows verification is performed separately; Linux CI does not test WebView2.

## Case-file GUI acceptance

| Check | Executed result |
|---|---|
| Clean installed package | 122 tests passed from a clean source export at `2b963095`, using an installed wheel without source-tree imports |
| Final layout | `94470158` changed four CSS lines; the wheel was rebuilt, all three GUI assets matched source, and both browser workflows passed again |
| Backend and migrations | Section conflicts/history; tag normalization; unknown dates; Intel provenance; Coworker + Friend together, independently ended/restarted; completion cycles |
| Browser | Directory, collapse without losing drafts, failed saves, duplicate names, section Edit/Append/History, photos, tags, multiple participants, Intel corrections, relationship episodes, reload, 1024/1440 layouts |
| SQLite restoration | A consistent backup of a fictional v4 fixture restored and migrated to schema 10; original IDs/text and foreign keys checked |
| Native Windows candidate | Packaged pywebview rendered Dashboard, People and Intel; native screenshots and Windows UI Automation verified controls |
| Portable move and restart | Copied executable saved a fictional record/photo, closed, moved to a renamed folder containing spaces, reopened and retrieved both |
| Earlier candidate ZIP | Manifest and ZIP hashes verified; no database present |

The native checks verify launch, rendering, database selection and persistence through the packaged
HTTP API. The complete browser click/form sequence was not repeated through Windows UI Automation.
[Application screenshots and workflow recording](demo/README.md) are captured from this verified GUI.
Publication changes add packaging, documentation and fictional fixture cleanup without changing its
application code. The release's embedded manifest identifies its exact clean build commit.

## Preservation and publication review

Personal data is preserved in private installation backups and consistent SQLite snapshots. Restored
copies passed integrity checks. No personal database is an input to application tests, builds or demo
seeding. Databases are never merged automatically.

A bounded all-ref scan found no tracked database/executable/archive files and no recognized credential
or private-key patterns. Full-name collisions with the private workspace were confined to historical
examples already represented in public prototype history. Current matching examples were replaced with
fictional names. This is not a guarantee that every historical prose fragment is insensitive; archived
commits remain public and have not been rewritten. See [publication contents](publication.md).

## Repeat the checks

Use the test and package commands in the [README](../README.md). On Windows, validate a copied release:

```powershell
.venv/Scripts/python scripts/verify_windows.py --exe <release>/netops/netops-gui/netops-gui.exe --output artifacts/new-native-check
```

Choose a new output directory. The script seeds fictional data, checks rendered controls, saves a record
and photo, closes the window, renames the copy and checks it again. Local logs and private backup manifests
are retained outside tracked content; they are not public download links. PyInstaller optional-platform
warnings are assessed against the actual Windows checks, not treated as desktop test results.
