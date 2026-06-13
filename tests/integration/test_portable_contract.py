from __future__ import annotations

from pathlib import Path


def test_portable_build_creates_data_and_profile_photo_asset_directories():
    script = Path("scripts/build-portable.ps1").read_text()
    portable_entry = Path("src/netops/portable.py").read_text()

    assert 'Join-Path $OutputDir "data"' in script
    assert 'Join-Path $OutputDir "data\\assets\\profile_photos"' in script
    assert "data\" / \"assets\" / \"profile_photos" in portable_entry
