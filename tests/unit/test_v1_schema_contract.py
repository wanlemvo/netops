from __future__ import annotations

from netops.storage import NetOpsRepository, connect
from netops.storage.migrations import SCHEMA_VERSION, current_version


def table_columns(connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def index_names(connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row["name"] for row in rows}


def test_v1_schema_tables_columns_and_no_standalone_notes(isolated_db):
    connection = connect(isolated_db)
    NetOpsRepository(connection)

    assert current_version(connection) == SCHEMA_VERSION
    tables = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }

    assert {
        "people",
        "contact_methods",
        "interactions",
        "interaction_people",
        "signals",
        "opportunities",
        "opportunity_people",
        "relationship_links",
        "tags",
        "taggings",
    }.issubset(tables)
    assert "notes" not in tables

    assert {
        "person_id",
        "name",
        "profile_photo_path",
        "relationship_status",
        "relationship_strength",
        "origin_story",
        "importance_reason",
        "dossier",
        "current_goals",
        "potential_value",
        "first_met",
        "last_contact",
        "next_action",
        "follow_up_date",
        "archived_at",
    }.issubset(table_columns(connection, "people"))
    assert "mutual_connections" not in table_columns(connection, "people")

    assert {
        "contact_method_id",
        "person_id",
        "type",
        "label",
        "value",
        "normalized_value",
        "is_primary",
        "archived_at",
    }.issubset(table_columns(connection, "contact_methods"))

    assert {"interaction_id", "interaction_date", "summary", "takeaways", "action_items"}.issubset(
        table_columns(connection, "interactions")
    )
    assert {"signal_id", "person_id", "signal_text", "source_interaction_id"}.issubset(
        table_columns(connection, "signals")
    )


def test_v1_schema_indexes_exist(isolated_db):
    connection = connect(isolated_db)
    NetOpsRepository(connection)

    indexes = index_names(connection)
    assert "idx_people_person_id_v1" in indexes
    assert "idx_contact_methods_person_type" in indexes
    assert "idx_interaction_people_person" in indexes
    assert "idx_signals_person" in indexes
    assert "idx_opportunity_people_person" in indexes
    assert "idx_relationship_links_source" in indexes
