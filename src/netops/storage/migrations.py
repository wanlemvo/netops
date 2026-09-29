from __future__ import annotations

import sqlite3


SCHEMA_VERSION = 10


MIGRATIONS: list[tuple[int, str]] = [
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS people (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            given_name TEXT,
            family_name TEXT,
            primary_email TEXT,
            primary_phone TEXT,
            organization TEXT,
            tags TEXT NOT NULL DEFAULT '[]',
            relationship_notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            related_person_id TEXT REFERENCES people(id) ON DELETE SET NULL,
            relationship_type TEXT NOT NULL,
            strength TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            occurred_on TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            notes TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS open_loops (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            source_interaction_id TEXT REFERENCES interactions(id) ON DELETE SET NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            due_on TEXT,
            priority INTEGER,
            resolution_notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            closed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS suggested_actions (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            open_loop_id TEXT REFERENCES open_loops(id) ON DELETE SET NULL,
            action_text TEXT NOT NULL,
            reason TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            status TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            acted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS evaluations (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            suggested_action_id TEXT REFERENCES suggested_actions(id) ON DELETE SET NULL,
            interaction_id TEXT REFERENCES interactions(id) ON DELETE SET NULL,
            outcome TEXT NOT NULL,
            impact_notes TEXT,
            evaluated_on TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_people_display_name ON people(display_name);
        CREATE INDEX IF NOT EXISTS idx_interactions_person_date ON interactions(person_id, occurred_on DESC);
        CREATE INDEX IF NOT EXISTS idx_open_loops_person_status ON open_loops(person_id, status, due_on);
        CREATE INDEX IF NOT EXISTS idx_suggestions_person_status ON suggested_actions(person_id, status);
        CREATE INDEX IF NOT EXISTS idx_evaluations_person ON evaluations(person_id, evaluated_on DESC);
        """,
    ),
    (
        2,
        """
        ALTER TABLE people ADD COLUMN alias TEXT;
        ALTER TABLE people ADD COLUMN role TEXT;
        ALTER TABLE people ADD COLUMN location TEXT;
        ALTER TABLE people ADD COLUMN relationship_type TEXT;
        ALTER TABLE people ADD COLUMN relationship_strength TEXT;
        ALTER TABLE people ADD COLUMN birthday TEXT;
        ALTER TABLE people ADD COLUMN interests TEXT NOT NULL DEFAULT '[]';
        ALTER TABLE people ADD COLUMN communication_style TEXT;
        ALTER TABLE people ADD COLUMN preferences_notes TEXT;
        ALTER TABLE people ADD COLUMN signals TEXT NOT NULL DEFAULT '[]';

        CREATE TABLE IF NOT EXISTS person_notes (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            note TEXT NOT NULL,
            source TEXT,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_person_notes_person_created ON person_notes(person_id, created_at DESC);
        """,
    ),
    (
        3,
        """
        CREATE TABLE IF NOT EXISTS person_contacts (
            id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            kind TEXT NOT NULL,
            label TEXT,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_person_contacts_person_kind ON person_contacts(person_id, kind);
        """,
    ),
    (
        4,
        """
        ALTER TABLE people ADD COLUMN person_id TEXT;
        ALTER TABLE people ADD COLUMN name TEXT;
        ALTER TABLE people ADD COLUMN profile_photo_path TEXT;
        ALTER TABLE people ADD COLUMN relationship_status TEXT;
        ALTER TABLE people ADD COLUMN origin_story TEXT;
        ALTER TABLE people ADD COLUMN importance_reason TEXT;
        ALTER TABLE people ADD COLUMN dossier TEXT;
        ALTER TABLE people ADD COLUMN preferences TEXT;
        ALTER TABLE people ADD COLUMN current_goals TEXT;
        ALTER TABLE people ADD COLUMN potential_value TEXT;
        ALTER TABLE people ADD COLUMN first_met TEXT;
        ALTER TABLE people ADD COLUMN last_contact TEXT;
        ALTER TABLE people ADD COLUMN next_action TEXT;
        ALTER TABLE people ADD COLUMN follow_up_date TEXT;
        ALTER TABLE people ADD COLUMN archived_at TEXT;

        UPDATE people
        SET person_id = COALESCE(person_id, id),
            name = COALESCE(name, display_name);

        ALTER TABLE interactions ADD COLUMN interaction_id TEXT;
        ALTER TABLE interactions ADD COLUMN interaction_date TEXT;
        ALTER TABLE interactions ADD COLUMN summary TEXT;
        ALTER TABLE interactions ADD COLUMN takeaways TEXT;
        ALTER TABLE interactions ADD COLUMN action_items TEXT;
        ALTER TABLE interactions ADD COLUMN sentiment TEXT;
        ALTER TABLE interactions ADD COLUMN follow_up_required INTEGER NOT NULL DEFAULT 0;
        ALTER TABLE interactions ADD COLUMN follow_up_date TEXT;
        ALTER TABLE interactions ADD COLUMN archived_at TEXT;

        UPDATE interactions
        SET interaction_id = COALESCE(interaction_id, id),
            interaction_date = COALESCE(interaction_date, occurred_on),
            summary = COALESCE(summary, notes);

        CREATE TABLE IF NOT EXISTS contact_methods (
            contact_method_id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            label TEXT,
            value TEXT NOT NULL,
            normalized_value TEXT,
            is_primary INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        );

        CREATE TABLE IF NOT EXISTS interaction_people (
            interaction_person_id TEXT PRIMARY KEY,
            interaction_id TEXT NOT NULL REFERENCES interactions(id) ON DELETE CASCADE,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            role TEXT,
            is_primary INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(interaction_id, person_id)
        );

        CREATE TABLE IF NOT EXISTS signals (
            signal_id TEXT PRIMARY KEY,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            signal_text TEXT NOT NULL,
            confidence TEXT,
            source_interaction_id TEXT REFERENCES interactions(id) ON DELETE SET NULL,
            source_description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        );

        CREATE TABLE IF NOT EXISTS opportunities (
            opportunity_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            follow_up_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            closed_at TEXT,
            archived_at TEXT
        );

        CREATE TABLE IF NOT EXISTS opportunity_people (
            opportunity_person_id TEXT PRIMARY KEY,
            opportunity_id TEXT NOT NULL REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
            person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
            role TEXT,
            is_primary INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(opportunity_id, person_id)
        );

        CREATE TABLE IF NOT EXISTS relationship_links (
            relationship_link_id TEXT PRIMARY KEY,
            source_entity_type TEXT NOT NULL,
            source_entity_id TEXT NOT NULL,
            target_entity_type TEXT NOT NULL,
            target_entity_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tags (
            tag_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        );

        CREATE TABLE IF NOT EXISTS taggings (
            tagging_id TEXT PRIMARY KEY,
            tag_id TEXT NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(tag_id, entity_type, entity_id)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_people_person_id_v1 ON people(person_id);
        CREATE INDEX IF NOT EXISTS idx_people_name_v1 ON people(name);
        CREATE INDEX IF NOT EXISTS idx_interactions_interaction_id_v1 ON interactions(interaction_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_date_v1 ON interactions(interaction_date);
        CREATE INDEX IF NOT EXISTS idx_interactions_follow_required_v1 ON interactions(follow_up_required);
        CREATE INDEX IF NOT EXISTS idx_interactions_follow_up_v1 ON interactions(follow_up_date);
        CREATE INDEX IF NOT EXISTS idx_interactions_archived_v1 ON interactions(archived_at);
        CREATE INDEX IF NOT EXISTS idx_people_org_v1 ON people(organization);
        CREATE INDEX IF NOT EXISTS idx_people_relationship_type_v1 ON people(relationship_type);
        CREATE INDEX IF NOT EXISTS idx_people_relationship_status_v1 ON people(relationship_status);
        CREATE INDEX IF NOT EXISTS idx_people_follow_up_date_v1 ON people(follow_up_date);
        CREATE INDEX IF NOT EXISTS idx_people_archived_at_v1 ON people(archived_at);
        CREATE INDEX IF NOT EXISTS idx_contact_methods_person ON contact_methods(person_id);
        CREATE INDEX IF NOT EXISTS idx_contact_methods_type ON contact_methods(type);
        CREATE INDEX IF NOT EXISTS idx_contact_methods_normalized ON contact_methods(normalized_value);
        CREATE INDEX IF NOT EXISTS idx_contact_methods_person_type ON contact_methods(person_id, type);
        CREATE INDEX IF NOT EXISTS idx_interaction_people_interaction ON interaction_people(interaction_id);
        CREATE INDEX IF NOT EXISTS idx_interaction_people_person ON interaction_people(person_id);
        CREATE INDEX IF NOT EXISTS idx_signals_person ON signals(person_id);
        CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source_interaction_id);
        CREATE INDEX IF NOT EXISTS idx_signals_confidence ON signals(confidence);
        CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at);
        CREATE INDEX IF NOT EXISTS idx_signals_archived ON signals(archived_at);
        CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
        CREATE INDEX IF NOT EXISTS idx_opportunities_follow_up ON opportunities(follow_up_date);
        CREATE INDEX IF NOT EXISTS idx_opportunities_archived ON opportunities(archived_at);
        CREATE INDEX IF NOT EXISTS idx_opportunity_people_opportunity ON opportunity_people(opportunity_id);
        CREATE INDEX IF NOT EXISTS idx_opportunity_people_person ON opportunity_people(person_id);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_source_type ON relationship_links(source_entity_type);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_source_id ON relationship_links(source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_target_type ON relationship_links(target_entity_type);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_target_id ON relationship_links(target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_type ON relationship_links(relationship_type);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_source ON relationship_links(source_entity_type, source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_target ON relationship_links(target_entity_type, target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_relationship_links_pair_type ON relationship_links(source_entity_id, target_entity_id, relationship_type);
        CREATE INDEX IF NOT EXISTS idx_taggings_tag ON taggings(tag_id);
        CREATE INDEX IF NOT EXISTS idx_taggings_entity_type ON taggings(entity_type);
        CREATE INDEX IF NOT EXISTS idx_taggings_entity_id ON taggings(entity_id);

        INSERT OR IGNORE INTO contact_methods (
            contact_method_id, person_id, type, label, value, normalized_value, is_primary, created_at, updated_at
        )
        SELECT id, person_id, kind, label, value, lower(value), 0, created_at, updated_at
        FROM person_contacts;

        INSERT OR IGNORE INTO contact_methods (
            contact_method_id, person_id, type, label, value, normalized_value, is_primary, created_at, updated_at
        )
        SELECT lower(hex(randomblob(16))), id, 'email', 'primary', primary_email, lower(primary_email), 1, created_at, updated_at
        FROM people
        WHERE primary_email IS NOT NULL AND trim(primary_email) != '';

        INSERT OR IGNORE INTO contact_methods (
            contact_method_id, person_id, type, label, value, normalized_value, is_primary, created_at, updated_at
        )
        SELECT lower(hex(randomblob(16))), id, 'phone', 'primary', primary_phone, primary_phone, 1, created_at, updated_at
        FROM people
        WHERE primary_phone IS NOT NULL AND trim(primary_phone) != '';

        INSERT OR IGNORE INTO interaction_people (
            interaction_person_id, interaction_id, person_id, role, is_primary, created_at
        )
        SELECT lower(hex(randomblob(16))), id, person_id, 'primary', 1, created_at
        FROM interactions;

        INSERT OR IGNORE INTO relationship_links (
            relationship_link_id, source_entity_type, source_entity_id, target_entity_type, target_entity_id,
            relationship_type, description, created_at, updated_at
        )
        SELECT id, 'person', person_id, 'person', related_person_id, relationship_type, notes, created_at, updated_at
        FROM relationships
        WHERE related_person_id IS NOT NULL;
        """,
    ),
]


MIGRATIONS.append((5, """
ALTER TABLE people ADD COLUMN follow_up_completed_at TEXT;
ALTER TABLE interactions ADD COLUMN follow_up_completed_at TEXT;
ALTER TABLE opportunities ADD COLUMN follow_up_completed_at TEXT;
UPDATE interactions SET follow_up_required = 1
WHERE trim(COALESCE(follow_up_date, '')) != '' AND follow_up_required = 0;
CREATE TRIGGER reopen_person_follow_up AFTER UPDATE OF follow_up_date, next_action ON people
WHEN OLD.follow_up_date IS NOT NEW.follow_up_date OR OLD.next_action IS NOT NEW.next_action
BEGIN UPDATE people SET follow_up_completed_at = NULL WHERE id = NEW.id; END;
CREATE TRIGGER reopen_interaction_follow_up AFTER UPDATE OF follow_up_date, follow_up_required ON interactions
WHEN OLD.follow_up_date IS NOT NEW.follow_up_date OR OLD.follow_up_required IS NOT NEW.follow_up_required
BEGIN UPDATE interactions SET follow_up_completed_at = NULL WHERE id = NEW.id; END;
CREATE TRIGGER reopen_opportunity_follow_up AFTER UPDATE OF follow_up_date ON opportunities
WHEN OLD.follow_up_date IS NOT NEW.follow_up_date
BEGIN UPDATE opportunities SET follow_up_completed_at = NULL WHERE opportunity_id = NEW.opportunity_id; END;
"""))


MIGRATIONS.append((6, """
CREATE TABLE dossier_sections (
    section_id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    format TEXT NOT NULL DEFAULT 'plain',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX idx_dossier_sections_person ON dossier_sections(person_id, created_at);
CREATE TABLE dossier_revisions (
    revision_id TEXT PRIMARY KEY,
    section_id TEXT NOT NULL REFERENCES dossier_sections(section_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    format TEXT NOT NULL,
    revision INTEGER NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE(section_id, revision)
);
"""))


MIGRATIONS.append((7, """
CREATE TABLE vocabulary (
    type_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    label TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(kind, normalized_name)
);
"""))


MIGRATIONS.append((8, """
ALTER TABLE signals ADD COLUMN intel_type TEXT NOT NULL DEFAULT 'Signal';
ALTER TABLE signals ADD COLUMN event_date TEXT;
ALTER TABLE signals ADD COLUMN source_date TEXT;
ALTER TABLE signals ADD COLUMN origin TEXT;
ALTER TABLE signals ADD COLUMN creator TEXT;
ALTER TABLE signals ADD COLUMN revision INTEGER NOT NULL DEFAULT 1;
CREATE TABLE intel_revisions (
    revision_id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL REFERENCES signals(signal_id) ON DELETE CASCADE,
    revision INTEGER NOT NULL,
    snapshot TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE(signal_id, revision)
);
"""))


MIGRATIONS.append((9, """
ALTER TABLE relationship_links ADD COLUMN started_on TEXT;
ALTER TABLE relationship_links ADD COLUMN ended_on TEXT;
ALTER TABLE relationship_links ADD COLUMN revision INTEGER NOT NULL DEFAULT 1;
CREATE TABLE relationship_revisions (
    revision_id TEXT PRIMARY KEY,
    relationship_link_id TEXT NOT NULL REFERENCES relationship_links(relationship_link_id) ON DELETE CASCADE,
    revision INTEGER NOT NULL,
    snapshot TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE(relationship_link_id, revision)
);
"""))


_completion_sql = '''CREATE TABLE follow_up_completions (
    event_id TEXT PRIMARY KEY, kind TEXT NOT NULL, record_id TEXT NOT NULL,
    person_ids TEXT NOT NULL, action TEXT, scheduled_date TEXT, completed_at TEXT NOT NULL
);'''
for _kind, _table, _key, _people, _action in [
    ('person', 'people', 'person_id', 'json_array(NEW.person_id)', 'NEW.next_action'),
    ('interaction', 'interactions', 'interaction_id', "(SELECT json_group_array(person_id) FROM interaction_people WHERE interaction_id=NEW.interaction_id)", 'COALESCE(NEW.action_items,NEW.summary)'),
    ('opportunity', 'opportunities', 'opportunity_id', "(SELECT json_group_array(person_id) FROM opportunity_people WHERE opportunity_id=NEW.opportunity_id)", 'NEW.title'),
]:
    _completion_sql += f'''
    INSERT INTO follow_up_completions SELECT lower(hex(randomblob(16))), '{_kind}', NEW.{_key}, {_people}, {_action}, NEW.follow_up_date, NEW.follow_up_completed_at
        FROM {_table} AS NEW WHERE NEW.follow_up_completed_at IS NOT NULL;
    CREATE TRIGGER record_{_kind}_completion AFTER UPDATE OF follow_up_completed_at ON {_table}
    WHEN OLD.follow_up_completed_at IS NULL AND NEW.follow_up_completed_at IS NOT NULL
    BEGIN
        INSERT INTO follow_up_completions VALUES (lower(hex(randomblob(16))), '{_kind}', NEW.{_key}, {_people}, {_action}, NEW.follow_up_date, NEW.follow_up_completed_at);
    END;
    '''
MIGRATIONS.append((10, _completion_sql))


def current_version(connection: sqlite3.Connection) -> int:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    row = connection.execute("SELECT MAX(version) AS version FROM schema_version").fetchone()
    return int(row["version"] or 0)


def migrate(connection: sqlite3.Connection) -> None:
    applied = current_version(connection)
    for version, script in MIGRATIONS:
        if version > applied:
            try:
                connection.executescript(f"BEGIN IMMEDIATE;\n{script}")
                if version == 7:
                    from netops.storage.catalog import backfill_catalog
                    backfill_catalog(connection)
                connection.execute('INSERT INTO schema_version(version) VALUES (?)', (version,))
                connection.commit()
            except Exception:
                connection.rollback()
                raise
