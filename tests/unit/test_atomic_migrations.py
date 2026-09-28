import pytest
import sqlite3
from netops.storage import connect, NetOpsRepository
from netops.storage import migrations


def test_failed_migration_rolls_back_schema_and_version(tmp_path, monkeypatch):
    connection = connect(tmp_path / 'fictional.sqlite3')
    NetOpsRepository(connection)
    version = migrations.current_version(connection)
    monkeypatch.setattr(migrations, 'MIGRATIONS', [*migrations.MIGRATIONS,
        (version + 1, 'ALTER TABLE people ADD COLUMN must_rollback TEXT; SELECT * FROM missing_table;')])
    with pytest.raises(sqlite3.OperationalError):
        migrations.migrate(connection)
    assert migrations.current_version(connection) == version
    assert 'must_rollback' not in {r['name'] for r in connection.execute('PRAGMA table_info(people)')}
    connection.close()
