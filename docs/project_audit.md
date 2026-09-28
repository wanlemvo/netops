# NetworkOps Documentation Audit

## 1. Documentation Inventory

### File: `README.md`

Purpose: Repository entry point and setup guide.

Key Decisions:

- NetworkOps is local-first.
- CLI/executable app is the main product surface.
- SQLite-backed data travels with the portable folder.
- Older TUI code still exists during cleanup.

Current Relevance: Useful for onboarding, but partially behind the V1 architecture direction. It still references existing CLI commands and portable build behavior rather than the full Person Intelligence Record model.

---

### File: `AGENTS.md`

Purpose: Agent/project instruction pointer.

Key Decisions:

- Current Spec Kit plan context is under `specs/003-dynamic-person-dossier/plan.md`.

Current Relevance: Partially outdated. The current active architecture work is `specs/004-person-intelligence-record`, so this pointer should eventually be updated after the V1 schema work is formalized.

---

### File: `docs/project-overview.md`

Purpose: High-level project summary.

Key Decisions:

- NetOps CLI is local-first.
- It preserves people, interaction context, follow-ups, suggestions, evaluations, and raw notes.
- CLI/executable workflow is emphasized over the older TUI.

Current Relevance: Still useful as a general overview, but it describes the pre-V1 dossier state and does not yet fully reflect the Person Intelligence Record model.

---

### File: `docs/architecture.md`

Purpose: Existing implementation architecture overview.

Key Decisions:

- Flow is CLI/executable -> Typer -> services -> domain/validation -> repositories -> SQLite.
- SQLite can live in `%USERPROFILE%/.netops` or portable `NETOPS_HOME/data`.
- Current schema concepts include people, person contacts, notes, relationships, interactions, open loops, suggestions, and evaluations.
- Suggestions are rule-based, not AI-generated.

Current Relevance: Required for understanding the current codebase, but not sufficient for V1 schema design. It should remain as "current implementation architecture" while `docs/architecture/networkops_v1_architecture.md` becomes the target architecture.

---

### File: `docs/architecture/networkops_v1_architecture.md`

Purpose: Target architecture for the Person Intelligence Record system.

Key Decisions:

- People are central.
- Contact methods, interaction logs, notes, signals, opportunities, and relationship links are separate entities.
- SQLite is recommended for local-first structured storage.
- Profile photos should be local assets with database references.
- Long-form text must be stored without truncation.
- Relationship links prepare for future graph-style connections.

Current Relevance: Required for schema implementation. This is the main architecture document for V1.

---

### File: `docs/data_model_v1.md`

Purpose: Entity and field definition before schema implementation.

Key Decisions:

- Primary records use UUID identity.
- Person `name` is required; most other person fields are optional.
- Contact methods are separate from people.
- Interaction logs, notes, signals, opportunities, and relationship links have their own fields.
- Tags are optional and should not replace controlled fields.
- Duplicate detection should warn, not block.

Current Relevance: Required for schema implementation. This is the strongest source for table and field design.

---

### File: `docs/adr/0001-use-sqlite-local-first.md`

Purpose: Storage strategy decision.

Key Decisions:

- Use SQLite for V1 structured storage.
- Keep data local-first and portable.
- No server, account, or cloud dependency is required.

Current Relevance: Required for schema implementation.

---

### File: `docs/adr/0002-separate-person-records-from-event-records.md`

Purpose: Boundary decision between person profiles and event/history records.

Key Decisions:

- People are separate from interaction logs, notes, signals, and opportunities.
- Person records summarize durable relationship intelligence.
- Event-based records grow independently over time.

Current Relevance: Required for schema implementation.

---

### File: `docs/adr/0003-store-profile-photos-as-local-assets.md`

Purpose: Profile photo storage decision.

Key Decisions:

- Store profile photos as local files.
- Store only a path/reference in the database.
- Handle missing or unsupported files gracefully.

Current Relevance: Required for schema implementation if profile-photo fields are included in V1 tables.

---

### File: `docs/adr/0004-support-long-form-multiline-text.md`

Purpose: Long-form text handling decision.

Key Decisions:

- Store long-form content without artificial truncation.
- Preserve pasted text and line breaks.
- Terminal size must not limit stored values.

Current Relevance: Required for schema and UI implementation.

---

### File: `docs/adr/0005-design-for-future-relationship-graph.md`

Purpose: Future graph-readiness decision.

Key Decisions:

- Include relationship-link concepts.
- Prepare for backlinks, cross-linking, and graph-like navigation.
- Do not implement graph visualization in V1.

Current Relevance: Required for relationship-link schema design, but future graph UX remains out of scope.

---

### File: `docs/adr/0006-person-identity-strategy.md`

Purpose: Person identity strategy.

Key Decisions:

- Use UUIDs as true identity.
- Names and contact methods are attributes.
- Duplicate detection should warn rather than prevent creation.

Current Relevance: Required for schema implementation.

---

### File: `docs/adr/0007-cross-linking-strategy.md`

Purpose: Cross-linking strategy.

Key Decisions:

- Use explicit relationship tables rather than text-only references.
- Initial links are manual.
- Initial relationships include person-note, person-interaction, person-signal, person-opportunity, and person-person.

Current Relevance: Required for relationship-link schema design.

---

### File: `docs/adr/0008-structured-fields-vs-tags.md`

Purpose: Classification strategy.

Key Decisions:

- Use structured fields for controlled-list values.
- Use tags only for flexible classification/discovery.
- Avoid tag sprawl for operational concepts.

Current Relevance: Required for schema design and validation choices.

---

### File: `docs/roadmap.md`

Purpose: Product and architecture roadmap.

Key Decisions:

- Keep CLI/executable workflow primary.
- Decide whether to remove/archive/separate TUI code.
- Improve contact management, notes, suggestions, backup/restore, and relationship edges.
- Future ideas include AI summaries, graph views, evidence-backed suggestions, and note promotion.

Current Relevance: Useful for future planning, but several items are future scope and should not drive V1 schema implementation.

---

### File: `docs/lessons-learned.md`

Purpose: Reflection document capturing product and architecture lessons.

Key Decisions:

- Profiles and interaction logs should be separate.
- Notes need contextual linking.
- NetworkOps is not a contact manager.
- The system requires graph-like relationships.
- Architecture matters earlier than expected.
- Portable data is part of the product.

Current Relevance: Highly relevant as product philosophy, but not a schema authority. Use it to validate direction, not to add new V1 scope.

---

### File: `docs/archive/model-selection-justification.md`

Purpose: Model/tool workflow reflection.

Key Decisions:

- Codex/GPT is best fit for implementation/debugging.
- Claude-style models are strong for planning.
- Gemini-style models are useful for research.
- Hybrid workflow is recommended.

Current Relevance: Historical/assignment artifact. Not relevant to V1 schema implementation.

---

### File: `docs/archive/portable-build.md`

Purpose: Portable Windows build guide.

Key Decisions:

- Portable folder contains `netops.exe` and `data/netops.sqlite3`.
- `NETOPS_HOME` points app data to the executable folder.

Current Relevance: Relevant to deployment and storage path choices. Some details may be outdated because README now shows `portable/netops-cli/`.

---

### File: `docs/archive/prompt-log.md`

Purpose: Curated development timeline.

Key Decisions:

- Project evolved from CLI to keyboard TUI to dynamic dossier.
- Additive migrations and append-only notes were used for dossier work.
- Advanced analytics and graph traversal were deferred.

Current Relevance: Historical. Useful for context, not a V1 schema source.

---

### File: `docs/archive/responsible-ai-analysis.md`

Purpose: AI risk analysis.

Key Decisions:

- Avoid unsupported AI-generated claims.
- Use tests and source artifacts as authority.
- Protect privacy in logs and summaries.

Current Relevance: Historical/assignment artifact. Not directly relevant to V1 schema implementation.

---

### File: `specs/004-person-intelligence-record/spec.md`

Purpose: Current V1 feature specification.

Key Decisions:

- NetworkOps becomes a Person Intelligence Record system.
- Person is central.
- Contact methods, interaction logs, notes, signals, opportunities, and relationship links are distinct concepts.
- Long-form text, profile photos, structured contact fields, and migration compatibility are required.
- AI, graph visualization, automation, and semantic search are future/non-goal areas.

Current Relevance: Primary requirements source for V1.

---

### File: `specs/004-person-intelligence-record/checklists/requirements.md`

Purpose: Quality checklist for the V1 feature spec.

Key Decisions:

- Confirms no clarification markers remain.
- Confirms requirements are testable and scope is bounded.

Current Relevance: Useful validation artifact. Not needed for schema details.

---

### File: `specs/003-dynamic-person-dossier/*`

Purpose: Previous dossier implementation spec, plan, contracts, tasks, and data model.

Key Decisions:

- Minimal person creation requires only name.
- Dossier fields are optional.
- Raw notes are separate and append-only.
- Last contact is derived from interactions.
- Existing data remains readable.

Current Relevance: Historical predecessor to V1. Useful for migration context and implemented behavior, but superseded by `004` for future schema direction.

---

### File: `specs/002-keyboard-tui-nav/*`

Purpose: Previous keyboard-driven terminal UI spec, plan, contracts, and data model.

Key Decisions:

- TUI navigation uses Up/Down/Enter/Escape.
- No command typing required for TUI navigation.
- Interaction-layer state is separate from persistent business entities.

Current Relevance: Relevant only if V1 implementation keeps or updates the TUI. Not a schema authority.

---

### File: `specs/001-netops-cli-app/*`

Purpose: Original NetOps CLI app spec, plan, contracts, and data model.

Key Decisions:

- Local-first CLI/TUI app.
- People, relationships, interactions, open loops, suggestions, and evaluations.
- Rule-based suggestions.
- SQLite persistence.

Current Relevance: Historical baseline. Important for migration compatibility but superseded by V1 architecture for new schema design.

---

### Directories: `docs/philosophy/` and `docs/research/`

Purpose: Requested in audit scope.

Key Decisions: No files currently exist in these paths.

Current Relevance: No current relevance. Philosophy is currently captured in `docs/lessons-learned.md`; research artifacts live mainly under `specs/*/research.md`.

## 2. Duplication Analysis

### Overlap: `specs/004-person-intelligence-record/spec.md` and `docs/architecture/networkops_v1_architecture.md`

Overlap Description: Both describe the core entities: Person, Contact Method, Interaction Log, Note, Signal, Opportunity, and Relationship Link.

Recommendation: Keep product requirements and acceptance criteria in `spec.md`. Keep technical entity relationships and storage strategy in `networkops_v1_architecture.md`. Do not merge.

---

### Overlap: `docs/architecture/networkops_v1_architecture.md` and `docs/data_model_v1.md`

Overlap Description: Both contain table/data model drafts.

Recommendation: Treat `docs/data_model_v1.md` as the canonical field-level source. Keep `networkops_v1_architecture.md` as the architecture narrative and high-level table sketch.

---

### Overlap: `docs/data_model_v1.md` and ADRs 0006-0008

Overlap Description: The data model repeats UUID identity, cross-linking, and structured-fields-vs-tags decisions.

Recommendation: Keep the ADRs as decision records and keep the data model as the applied design. No merge needed.

---

### Overlap: `docs/lessons-learned.md` and `specs/004-person-intelligence-record/spec.md`

Overlap Description: Both state that NetworkOps is not just a contact manager and that profiles, interactions, notes, and graph-like relationships should be separate.

Recommendation: Keep `lessons-learned.md` as philosophy/history. Keep `spec.md` as the V1 requirement source.

---

### Overlap: `docs/roadmap.md` and `specs/004-person-intelligence-record/spec.md`

Overlap Description: Both mention future graph views, AI summaries, note promotion, and relationship intelligence.

Recommendation: Keep future ideas in roadmap only. Ensure V1 spec and schema docs continue to mark AI, semantic search, graph visualization, and automation as non-goals.

---

### Overlap: `docs/architecture.md` and `docs/architecture/networkops_v1_architecture.md`

Overlap Description: Both describe architecture, storage, and schema concepts, but one describes current implementation and the other describes target V1.

Recommendation: Rename or clarify later: `docs/architecture.md` should be "current architecture" and `networkops_v1_architecture.md` should be "target V1 architecture." Do not merge before schema work.

---

### Overlap: `specs/003-dynamic-person-dossier/data-model.md` and `docs/data_model_v1.md`

Overlap Description: Both define person/dossier fields and notes.

Recommendation: Keep `003` as historical implementation context. Use `docs/data_model_v1.md` for new schema design.

---

### Overlap: `docs/archive/portable-build.md` and `README.md`

Overlap Description: Both describe portable build layout and data persistence.

Recommendation: Keep README as current user-facing guide. Treat archived portable doc as historical unless reconciled later.

## 3. Missing Architecture Pieces

### Person

Status: Documented.

Why: Defined in `spec.md`, `networkops_v1_architecture.md`, `docs/data_model_v1.md`, ADR 0002, and ADR 0006. Fields, identity strategy, required name, optional fields, timestamps, and migration expectations are covered.

### Contact Method

Status: Documented.

Why: Defined as separate from person in architecture and data model. Fields include type, label, value, normalized value, primary flag, timestamps, and archive marker.

### Interaction Log

Status: Partially documented.

Why: Core fields are documented, including summary, takeaways, action items, sentiment, follow-up, created/updated/archive timestamps. The remaining ambiguity is whether V1 schema uses only `person_id`, only relationship links, or both for person associations. Current docs suggest `person_id` for primary person plus future links.

### Signal

Status: Documented.

Why: Defined as separate entity with signal text, confidence, source entity, optional person association, and timestamps. Source modeling is present but will need SQL-level constraints during schema design.

### Opportunity

Status: Documented.

Why: Defined with title, status, person association, owner person, description, follow-up date, and lifecycle timestamps. Status vocabulary is suggested.

### Relationship Link

Status: Partially documented.

Why: The relationship-link concept and fields are documented. The missing detail is the exact SQL integrity strategy for polymorphic links: allowed entity types, how to validate target IDs, whether links are directional or should be normalized for bidirectional use, and whether duplicate links are allowed.

## 4. Data Model Readiness Assessment

Can a complete SQLite schema be designed from the current documentation?

Mostly yes, but one more schema-focused artifact is needed before implementation.

What is ready:

- Entity list is complete.
- Most field names are defined.
- UUID identity strategy is defined.
- Local-first SQLite decision is made.
- Profile photo path strategy is defined.
- Long-form text strategy is defined.
- Migration expectations are defined.
- V1 non-goals are clear.

What is still missing for a complete SQLite schema:

- Exact SQLite column types for every field.
- Required versus optional/nullability for every non-person field.
- Default values for timestamps, booleans, statuses, and archive fields.
- Exact primary key naming convention: `id` versus `person_id`, `note_id`, etc.
- Foreign key behavior for delete/archive cases.
- Unique indexes and duplicate-warning support indexes.
- Controlled vocabulary enforcement approach: CHECK constraints, lookup tables, or application validation.
- Exact `relationship_links` integrity rules for polymorphic entity references.
- Exact tag strategy for V1: simple person tag text, normalized `tags/taggings`, or both.
- Date storage format and validation convention.
- Profile photo path storage convention: relative to data root, asset root, or app root.
- Migration ordering from current tables to V1 tables.
- Backward compatibility mapping from current tables such as `person_contacts`, `person_notes`, `interactions`, `open_loops`, `suggested_actions`, and `evaluations`.

Conclusion: The data model is ready for schema design, but not ready to skip directly into migrations.

## 5. Implementation Readiness Assessment

Current Stage: Data Model.

Justification:

- Research exists in older Spec Kit artifacts and product lessons.
- Requirements exist in `specs/004-person-intelligence-record/spec.md`.
- Architecture exists in `docs/architecture/networkops_v1_architecture.md`.
- ADRs exist for major storage, entity, identity, linking, text, media, graph-readiness, and classification decisions.
- A V1 data model exists in `docs/data_model_v1.md`.
- A concrete SQLite schema does not yet exist.
- A migration plan does not yet exist.
- No V1 schema implementation should begin until the exact table definitions, constraints, indexes, and migration mapping are written.

Therefore, the project is past architecture/ADR and currently at Data Model, with Schema Design as the next stage.

## 6. Recommended Next Artifact

Recommended Next Artifact: `docs/schema_v1.md`

Why:

The shortest path to implementation is to convert the current data model into an exact SQLite schema. The repo already has enough requirements, architecture, ADRs, and entity modeling. Creating more philosophy or architecture docs would add little value before schema work.

`docs/schema_v1.md` should define:

- Exact table names.
- Exact columns.
- SQLite types.
- Required/optional fields.
- Primary keys.
- Foreign keys.
- CHECK constraints or validation strategy.
- Indexes.
- Timestamp conventions.
- Archive/delete behavior.
- Relationship-link validation rules.
- Tag implementation choice.
- Legacy-to-V1 mapping notes.

This should come before `migration_plan.md` because migration planning needs a concrete target schema.

## 7. Scope Creep Detection

### NetOps V1

Belongs in V1:

- Person Intelligence Record.
- Structured contact methods.
- Interaction logs.
- Standalone notes.
- Signals.
- Opportunities.
- Relationship links as explicit records.
- UUID person identity.
- Duplicate detection warnings.
- SQLite local-first storage.
- Profile photo local file references.
- Long-form multiline text storage.
- Controlled fields where values are operational.
- Tags for flexible discovery.
- Migration compatibility for existing local records.

These are aligned with the current V1 spec and required for schema implementation.

### Future NetOps

Belongs in future NetOps:

- Natural language entry.
- Hyperlink-style experiences.
- Backlink browsing.
- Multiple participants per interaction beyond V1 primary-person behavior.
- Knowledge graph navigation.
- Graph visualization.
- Evidence-backed suggestions.
- Automatic promotion of raw notes into structured fields.
- Advanced duplicate resolution/merge workflows.
- Export/backup/restore improvements beyond basic local persistence.

These should remain visible in roadmap/future sections but should not expand the V1 schema beyond explicit link-readiness.

### Solo

Belongs to Solo, not NetOps V1:

- Broader personal operating-system workflows.
- Goals, projects, decisions, learning, and execution planning outside relationship intelligence.
- Solo module integration.

Solo integration is correctly listed as future consideration. It should not influence V1 tables except by preserving clean entity boundaries.

### External Systems

Belongs outside V1:

- Obsidian integration.
- Notion integration.
- Gmail/email integration.
- Calendar integration.
- Social media or OSINT automation.
- Cloud CRM sync.

Obsidian, Notion, Wikipedia, Salesforce, and HubSpot are useful design influences, but not dependencies or integrations for V1.

### Scope Pollution Risks

AI recommendations: Out of V1. The current docs correctly mark AI as future/non-goal. Keep rule-based suggestions from existing system separate from any AI feature.

Semantic search: Out of V1. It should not drive schema design beyond preserving text and links.

Graph visualization: Out of V1. Relationship links should prepare for it, but no visualization should be implemented.

Knowledge management: Partially in scope. Notes and links are in V1, but a full Obsidian-like knowledge system is future scope.

OSINT automation: Out of V1. Contact methods and social fields are user-entered attributes, not automated enrichment targets.

Automation: Out of V1. Follow-up dates and next actions are in scope as stored data; automated reminders/workflows are not.

Recommendation systems: Out of V1. Existing rule-based suggestions may remain part of current app behavior, but the V1 schema pass should not add recommender architecture.

## Final Audit Conclusion

The documentation is strong enough to proceed to schema design. The current blocker is not missing product vision or architecture direction. The blocker is the absence of an exact SQLite schema document that resolves column types, constraints, indexes, relationship-link validation, tag strategy, and migration mapping.

Shortest path:

1. Create `docs/schema_v1.md`.
2. Create `docs/migration_plan.md`.
3. Implement schema and migrations.
4. Update domain, repository, and service layers.
5. Add focused tests for migration compatibility, long-form text, contact methods, profile photos, and relationship links.
