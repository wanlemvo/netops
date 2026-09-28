from __future__ import annotations

import sqlite3


SCHEMA_VERSION = 2


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
]


def current_version(connection: sqlite3.Connection) -> int:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    row = connection.execute("SELECT MAX(version) AS version FROM schema_version").fetchone()
    return int(row["version"] or 0)


def migrate(connection: sqlite3.Connection) -> None:
    applied = current_version(connection)
    with connection:
        for version, script in MIGRATIONS:
            if version > applied:
                connection.executescript(script)
                connection.execute("INSERT OR IGNORE INTO schema_version(version) VALUES (?)", (version,))
