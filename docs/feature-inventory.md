# Current feature and workflow inventory

Evidence refers to the case-file iteration. Browser controls are exercised in Microsoft Edge;
native packaging and desktop rendering are checked separately.

| Workflow | Current GUI / backend | Evidence |
|---|---|---|
| Navigation | Collapsible persistent nav, full People directory/profile, global + New | Browser: retained tabs/drafts, no reload on collapse, saved preference |
| Person creation/search | Duplicate names retain IDs; filtered creation opens new record | Backend and browser |
| Dossier reading/editing | Safe Markdown reading; section Edit/Add/Append; preserved history | Rendering, conflict, revision and browser tests |
| Current context | Separate ordinary forms for goals, interests, preferences and communication | Backend validation; browser section controls |
| Photos | PNG/JPEG/WebP preview/import/replace/remove; relative assets; initials fallback | Service and browser; renamed-directory fixture |
| Tags | Persistent canonical assignments, search/check/create, usage page | Legacy union migration and browser |
| Types | Reusable defaults/custom interaction and relationship types; normalized case/spacing | Repository and browser |
| Interactions | Global/profile multi-person events, local date, summary/takeaways/actions | Browser, shared participant and invalid-date regression |
| Intel | Typed content, provenance, two dates, optional interaction, revisions | Legacy preservation, stale-edit, reference validation and browser |
| Relationships | Directed endpoints; independent simultaneous typed episodes; start/end/history | Coworker + Friend + end + re-add regression and browser |
| Follow-ups | Person/interaction/opportunity pending actions, complete/reschedule | Idempotency, restart, preserved completion-cycle tests |
| Timeline | Derived events; recorded/source/event labels; no imported-prose fabrication | Chronology regression and browser |
| Contacts/opportunities | Existing Add/browse profile flows retained | Existing backend/API/browser suite |
| Portable storage | Marker/sibling layout, overrides, ambiguity errors, visible path | Existing path tests and copied portable checks |
| Network Map | Disabled future destination | Source/browser inspection |
| Analytics | Absent from navigation | Source inspection |
| CLI/TUI | Secondary historical tools retained; no new parity contract | Existing regression suite |

There is no AI, cloud synchronization, remote service, encryption or graph visualization.
See [verification](verification.md) and [implementation boundaries](casefile-iteration.md).
