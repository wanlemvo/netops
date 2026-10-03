"""Public demo is generated from controlled fixtures, never an existing database."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import zipfile

import pytest


def test_demo_archive_isolated_fictional_database(tmp_path):
    script = Path(__file__).resolve().parents[2] / 'scripts/build_release.py'
    spec = importlib.util.spec_from_file_location('release_builder', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / 'netops-0.2.0-fixture'
    portable = output / 'netops'
    portable.mkdir(parents=True)
    (portable / '.netops-portable').write_text('NetOps portable root v1\n')
    (portable / 'build-manifest.json').write_text(json.dumps({'source_commit': 'fixture', 'build': {'personal_data': False}}))
    archive = module.build_demo(output)
    assert archive.name == 'netops-0.2.0-fixture-demo.zip'
    assert not (portable / 'data/netops.sqlite3').exists()
    with zipfile.ZipFile(archive) as bundle:
        assert [n for n in bundle.namelist() if n.endswith('.sqlite3')] == ['netops/data/netops.sqlite3']
        assert b'NETOPS_DB=%~dp0data\\netops.sqlite3' in bundle.read('netops/Open NetOps.cmd')
        manifest = json.loads(bundle.read('netops/build-manifest.json'))
        assert manifest['source_commit'] == 'fixture'
        assert manifest['build']['personal_data'] is False
        for name, digest in manifest['sha256'].items():
            assert hashlib.sha256(bundle.read('netops/' + name)).hexdigest() == digest
    database = output.with_name(output.name + '-demo') / 'netops/data/netops.sqlite3'
    with sqlite3.connect(database) as connection:
        assert connection.execute('pragma integrity_check').fetchone()[0] == 'ok'
        assert {r[0] for r in connection.execute('select name from people')} == {'Avery Chen', 'Morgan Ellis'}
    (portable / 'unexpected.sqlite3').write_bytes(b'private fixture sentinel')
    with pytest.raises(RuntimeError, match='data-free'):
        module.build_demo(output)
