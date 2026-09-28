from __future__ import annotations

from pathlib import Path


def test_portable_build_creates_data_and_profile_photo_asset_directories():
    script = Path("scripts/build-portable.ps1").read_text()
    portable_entry = Path("src/netops/portable.py").read_text()
    portable_cli = Path("src/netops/portable_cli.py").read_text()
    portable_gui = Path("src/netops/portable_gui.py").read_text()

    assert '$LegacyPortableRoot = Join-Path $RepoRoot "portable"' in script
    assert '$DistRoot = Join-Path $RepoRoot "netops"' in script
    assert '$CliOutputDir = Join-Path $DistRoot "netops-cli"' in script
    assert '$GuiOutputDir = Join-Path $DistRoot "netops-gui"' in script
    assert '$SharedDataDir = Join-Path $DistRoot "data"' in script
    assert '$RepoDataDir = Join-Path $RepoRoot "data"' in script
    assert '$StagingRoot = Join-Path $RepoRoot ".netops-staging"' in script
    assert '$LegacySharedDataDir = Join-Path $LegacyDistRoot "data"' in script
    assert 'Join-Path $SharedDataDir "assets\\profile_photos"' in script
    assert '$GuiStaticDir = Join-Path $RepoRoot "src\\netops\\gui\\static"' in script
    assert '"--add-data", $GuiStaticData' in script
    assert 'Build-PortableExecutable -Name "netops-cli"' in script
    assert 'Build-PortableExecutable -Name "netops-gui"' in script
    assert "-IncludeGuiAssets -Windowed" in script
    assert '"pywebview>=6.2.1"' in Path("pyproject.toml").read_text()
    assert "Remove-OutputPath $LegacyPortableRoot" in script
    assert "data\" / \"assets\" / \"profile_photos" in portable_entry
    assert 'executable_dir.parent.name.lower() == "netops"' in portable_entry
    assert 'main(default_command="tui")' in portable_cli
    assert 'main(default_command="gui")' in portable_gui
