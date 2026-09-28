# Feature and workflow inventory

Status refers to the reconciled application. Browser tests exercise actual rendered controls;
API tests alone do not establish that a desktop window works.

| Workflow | Reference finding | Reconciled behavior | Evidence |
|---|---|---|---|
| Find/add/open person | New person was not selected; filtered state could obscure it | Search by identity/context; new record opens and filter clears | Browser workflow; backend tests |
| Edit dossier | Edit form existed without launch button | Visible Edit Person; atomic save; invalid input retains draft | Browser invalid-date test; rollback tests |
| Browse dossier records | Dynamic tab buttons lacked handlers and represented Add actions | Persistent event delegation; record tabs and separate Add buttons | Browser workflow |
| Log interaction | Date did not set required flag | Date implies follow-up; optional checkbox supports unscheduled follow-up | Service and browser tests |
| Review/complete follow-up | Dashboard query omitted interactions; no completion API | Person, interaction and opportunity follow-ups; durable completion and rescheduling | Migration, lifecycle and browser tests |
| Contact methods | Backend existed | Add and retrieve through Contact tab | Browser and API tests |
| Signals/opportunities/links | Backend existed, dossier controls incomplete | Add and retrieve through dedicated dossier tabs | Browser and contract tests |
| Profile photos | Absolute asset references could break after moving | New copies use relative references; legacy filename fallback | Copied-folder API test; CLI retained |
| Portable storage | Required outer folder name `netops` | Marker and existing sibling-data discovery; ambiguity errors | Path tests; distribution checks |
| Tags | Stored tags/filtering existed; dedicated page placeholder | Existing tags retained; dedicated page disabled | Code inspection and backend tests |
| Analytics/Map View | Placeholders | Disabled and marked planned | Browser/source inspection |
| Encryption/sync/clearance | Decorative claims | Accurate local SQLite/no-cloud description | Rendered screenshot |
| CLI/TUI/raw notes | Earlier functionality | Retained as secondary interfaces and legacy data | Existing regression suite |

No AI, cloud sync, graph visualization, encryption, or integration capability is claimed.
See verification.md for the executed results and native Windows verification boundary.
