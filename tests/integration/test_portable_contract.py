from pathlib import Path
import sys
import pytest
from netops.portable import portable_home

def test_renamed_portable_root(tmp_path, monkeypatch):
    root = tmp_path / "My renamed network"
    exe = root / "netops-gui" / "netops-gui.exe"
    exe.parent.mkdir(parents=True)
    (root / "data").mkdir()
    (root / "data/netops.sqlite3").touch()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe))
    assert portable_home() == root
    (exe.parent / "data").mkdir()
    (exe.parent / "data/netops.sqlite3").touch()
    with pytest.raises(RuntimeError, match="Multiple"):
        portable_home()

def test_marker_selects_clean_distribution(tmp_path, monkeypatch):
    exe = tmp_path / "netops-gui" / "netops-gui.exe"
    exe.parent.mkdir()
    (tmp_path / ".netops-portable").touch()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe))
    assert portable_home() == tmp_path
