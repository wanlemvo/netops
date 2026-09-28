# Architecture

The primary interface is the existing HTML/CSS/JavaScript GUI hosted in a pywebview EdgeChromium
window. A loopback Python HTTP server serves packaged assets and translates requests into the
NetworkOpsBackend facade. The facade uses shared people, interaction and follow-up services;
repositories handle SQLite mapping. CLI/TUI surfaces use the same underlying services.

```mermaid
flowchart LR
  Desktop[pywebview desktop] --> GUI[HTML / CSS / JavaScript]
  GUI --> HTTP[Loopback HTTP API]
  HTTP --> Backend[Shared application facade]
  Terminal[CLI / TUI] --> Services[Services and validation]
  Backend --> Services
  Services --> Repository[SQLite repository]
```

Each HTTP request owns and closes its database connection. Nested repository writes share the
outer service transaction, so compound person/contact saves roll back together. Migration scripts
and their version records commit atomically. Legacy tables and append-only raw notes are retained.

Schema 5 adds completion timestamps to people, interactions and opportunities. Completing a follow-up
preserves its original context; rescheduling clears completion. Person edits reset completion only
when schedule/action changes. Dated historical interactions are recovered into the pending list.
An opportunity follow-up can be completed without closing the opportunity itself.

The GUI delegates clicks from stable containers so newly rendered controls work. Tabs show records;
Add controls open forms. Errors retain draft input, pending submissions disable Save, and successful
creation selects the returned ID. Duplicate names remain distinct records.

New API operations: GET /api/settings reports the actual database file; POST
/api/follow-ups/{kind}/{id}/complete persists idempotent completion; PATCH
/api/follow-ups/{kind}/{id} changes follow_up_date. A null date retains an unscheduled interaction
follow-up; a person still needs a next action, and an opportunity without a date has no scheduled follow-up.
Kinds are person, interaction and opportunity. Unsupported kinds return 400; missing records 404.

Portable roots are selected using a marker or existing sibling data, independent of outer folder name.
Environment overrides take precedence. Ambiguous candidates stop startup. New photo copies use paths
relative to the database directory; moved legacy absolute references get an assets-directory fallback.

The application remains local and single-user. The HTTP bridge has no authentication or remote hosting
contract. Browser writes require JSON and a same-origin request. No cloud, encryption or AI service is
implemented. Retaining the service facade leaves a future integration boundary without adding one now.
