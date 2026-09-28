from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from types import SimpleNamespace

from netops.gui.server import NetOpsGuiServer, launch_gui
from netops.services.app_backend import NetworkOpsBackend
from netops.storage import NetOpsRepository, connect


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict, *, method: str = "POST"):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def backend_factory(db_path):
    return lambda: NetworkOpsBackend(NetOpsRepository(connect(db_path)))


def test_gui_server_serves_static_shell_and_api(v1_repository, isolated_db):
    backend = NetworkOpsBackend(v1_repository)
    person = backend.create_person({"name": "Henry Valentine", "organization": "T-Mobile"})
    server = NetOpsGuiServer(backend_factory=backend_factory(isolated_db), port=0)
    server.start_background()
    try:
        with urllib.request.urlopen(server.url, timeout=5) as response:
            html = response.read().decode("utf-8")
        people = get_json(f"{server.url}api/people")
        dossier = get_json(f"{server.url}api/people/{person['person_id']}/dossier")

        assert "NETOPS" in html
        assert people[0]["name"] == "Henry Valentine"
        assert dossier["header"]["title"] == "Henry Valentine"
    finally:
        server.stop()


def test_gui_server_write_flow_preserves_multiline_text(isolated_db):
    server = NetOpsGuiServer(backend_factory=backend_factory(isolated_db), port=0)
    server.start_background()
    try:
        person = post_json(
            f"{server.url}api/people",
            {
                "name": "Dr Olav",
                "organization": "T-Mobile",
                "dossier": "Line one.\nLine two.",
            },
        )
        post_json(
            f"{server.url}api/people/{person['person_id']}/signals",
            {"text": "Values direct follow-through.", "confidence": "high"},
        )
        updated = post_json(
            f"{server.url}api/people/{person['person_id']}",
            {"dossier": "Line one.\nLine two.\nLine three."},
            method="PATCH",
        )
        dossier = get_json(f"{server.url}api/people/{person['person_id']}/dossier")

        assert updated["dossier"] == "Line one.\nLine two.\nLine three."
        assert dossier["folder_payloads"]["signals"][0]["text"] == "Values direct follow-through."
    finally:
        server.stop()


def test_gui_server_reports_missing_profile_photo(v1_repository, isolated_db):
    backend = NetworkOpsBackend(v1_repository)
    person = backend.create_person({"name": "No Photo"})
    server = NetOpsGuiServer(backend_factory=backend_factory(isolated_db), port=0)
    server.start_background()
    try:
        try:
            urllib.request.urlopen(f"{server.url}api/people/{person['person_id']}/profile-photo", timeout=5)
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:  # pragma: no cover
            raise AssertionError("Expected missing profile photo to return 404.")
    finally:
        server.stop()


def test_gui_launcher_opens_native_desktop_window(monkeypatch, isolated_db):
    captured = {}

    def create_window(title, url, **kwargs):
        captured.update(title=title, url=url, window_options=kwargs)

    def start(**kwargs):
        captured["start_options"] = kwargs
        captured["overview"] = get_json(f"{captured['url']}api/overview")

    monkeypatch.setitem(sys.modules, "webview", SimpleNamespace(create_window=create_window, start=start))

    launch_gui(port=0)

    assert captured["title"] == "NetworkOps"
    assert captured["window_options"]["min_size"] == (1024, 680)
    assert captured["start_options"] == {"gui": "edgechromium", "debug": False}
    assert captured["overview"]["view"] == "overview"
