from __future__ import annotations

import json

from netops.cli import app


def test_profile_photo_existing_file_is_copied_to_local_assets(runner, isolated_db, tmp_path):
    runner.invoke(app, ["people", "add", "--name", "Avery Chen"])
    photo = tmp_path / "avery.png"
    photo.write_bytes(b"fake image bytes")

    result = runner.invoke(app, ["people", "photo", "Avery Chen", "--path", str(photo)])
    assert result.exit_code == 0, result.output

    shown = runner.invoke(app, ["people", "show", "Avery Chen", "--json"])
    payload = json.loads(shown.output)
    stored_path = payload["profile_photo_path"]

    assert stored_path.endswith(".png")
    assert "profile_photos" in stored_path
    assert isolated_db.parent.joinpath("assets", "profile_photos").exists()


def test_profile_photo_missing_file_keeps_reference_without_blocking_record(runner):
    runner.invoke(app, ["people", "add", "--name", "Missing Photo Person"])

    result = runner.invoke(app, ["people", "photo", "Missing Photo Person", "--path", "missing/photo.png"])
    assert result.exit_code == 0, result.output

    shown = runner.invoke(app, ["people", "show", "Missing Photo Person", "--json"])
    assert json.loads(shown.output)["profile_photo_path"] == "missing/photo.png"
