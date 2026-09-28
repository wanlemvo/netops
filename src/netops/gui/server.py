from __future__ import annotations

import json
import mimetypes
import threading
import webbrowser
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from netops.domain.validation import NetOpsError
from netops.services.app_backend import NetworkOpsBackend

JsonDict = dict[str, Any]


class NetOpsGuiServer:
    def __init__(
        self,
        backend: NetworkOpsBackend | None = None,
        backend_factory: Callable[[], NetworkOpsBackend] | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        if backend_factory is not None:
            self._backend_factory = backend_factory
        elif backend is not None:
            self._backend_factory = lambda: backend
        else:
            self._backend_factory = NetworkOpsBackend
        self.host = host
        self._httpd = ThreadingHTTPServer((host, port), self._handler())
        self._thread: threading.Thread | None = None

    @property
    def port(self) -> int:
        return int(self._httpd.server_address[1])

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/"

    def serve_forever(self) -> None:
        self._httpd.serve_forever()

    def start_background(self) -> None:
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def backend(self) -> NetworkOpsBackend:
        return self._backend_factory()

    def _handler(self):
        gui_server = self

        class NetOpsGuiRequestHandler(BaseHTTPRequestHandler):
            server_version = "NetOpsGui/0.1"

            def log_message(self, format: str, *args: object) -> None:
                return

            def do_GET(self) -> None:
                try:
                    self._route_get()
                except Exception as exc:  # pragma: no cover - defensive server boundary
                    self._send_error(exc)

            def do_POST(self) -> None:
                try:
                    self._route_write("POST")
                except Exception as exc:  # pragma: no cover - defensive server boundary
                    self._send_error(exc)

            def do_PATCH(self) -> None:
                try:
                    self._route_write("PATCH")
                except Exception as exc:  # pragma: no cover - defensive server boundary
                    self._send_error(exc)

            def _route_get(self) -> None:
                parsed = urlparse(self.path)
                path = parsed.path
                query = parse_qs(parsed.query)

                if path == "/api/overview":
                    self._send_json(gui_server.backend().get_overview())
                    return
                if path == "/api/workspace":
                    self._send_json(gui_server._workspace())
                    return
                if path == "/api/people":
                    search = _first_query(query, "search")
                    tag = _first_query(query, "tag")
                    self._send_json(gui_server.backend().list_people(search=search, tag=tag))
                    return
                if path.startswith("/api/people/") and path.endswith("/profile-photo"):
                    person_id = _path_part(path, 2)
                    self._send_profile_photo(person_id)
                    return
                if path.startswith("/api/people/") and path.endswith("/dossier"):
                    person_id = _path_part(path, 2)
                    self._send_json(gui_server.backend().get_dossier(person_id))
                    return
                if path.startswith("/api/people/"):
                    person_id = _path_part(path, 2)
                    self._send_json(gui_server.backend().get_person(person_id))
                    return

                self._send_static(path)

            def _route_write(self, method: str) -> None:
                path = urlparse(self.path).path
                payload = self._read_json()

                if method == "POST" and path == "/api/people":
                    self._send_json(gui_server.backend().create_person(payload), status=HTTPStatus.CREATED)
                    return
                if method == "PATCH" and path.startswith("/api/people/"):
                    person_id = _path_part(path, 2)
                    self._send_json(gui_server.backend().update_person(person_id, payload))
                    return
                if method == "POST" and path.startswith("/api/people/") and path.endswith("/contacts"):
                    person_id = _path_part(path, 2)
                    self._send_json(gui_server.backend().add_contact_method(person_id, payload), status=HTTPStatus.CREATED)
                    return
                if method == "POST" and path == "/api/interactions":
                    self._send_json(gui_server.backend().add_interaction(payload), status=HTTPStatus.CREATED)
                    return
                if method == "POST" and path.startswith("/api/people/") and path.endswith("/signals"):
                    person_id = _path_part(path, 2)
                    self._send_json(gui_server.backend().add_signal(person_id, payload), status=HTTPStatus.CREATED)
                    return
                if method == "POST" and path == "/api/opportunities":
                    self._send_json(gui_server.backend().add_opportunity(payload), status=HTTPStatus.CREATED)
                    return
                if method == "POST" and path == "/api/relationship-links":
                    self._send_json(gui_server.backend().add_relationship_link(payload), status=HTTPStatus.CREATED)
                    return

                self._send_json({"error": "Route not found."}, status=HTTPStatus.NOT_FOUND)

            def _send_profile_photo(self, person_id: str) -> None:
                dossier = gui_server.backend().get_dossier(person_id)
                photo_path = dossier.get("header", {}).get("profile_photo_path")
                if not photo_path:
                    self._send_json({"error": "Profile photo is not set."}, status=HTTPStatus.NOT_FOUND)
                    return
                path = Path(str(photo_path)).expanduser()
                if not path.exists() or not path.is_file():
                    self._send_json({"error": "Profile photo file was not found."}, status=HTTPStatus.NOT_FOUND)
                    return
                content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                data = path.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _send_static(self, request_path: str) -> None:
                relative = "index.html" if request_path in {"/", ""} else unquote(request_path).lstrip("/")
                if relative.startswith("api/") or ".." in Path(relative).parts:
                    self._send_json({"error": "Route not found."}, status=HTTPStatus.NOT_FOUND)
                    return
                static_root = resources.files("netops.gui.static")
                target = static_root.joinpath(relative)
                if not target.is_file():
                    target = static_root.joinpath("index.html")
                data = target.read_bytes()
                content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _read_json(self) -> JsonDict:
                length = int(self.headers.get("Content-Length", "0"))
                if not length:
                    return {}
                body = self.rfile.read(length).decode("utf-8")
                loaded = json.loads(body)
                if not isinstance(loaded, dict):
                    raise ValueError("Request body must be a JSON object.")
                return loaded

            def _send_json(self, payload: Any, *, status: HTTPStatus = HTTPStatus.OK) -> None:
                data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _send_error(self, exc: Exception) -> None:
                status = HTTPStatus.BAD_REQUEST if isinstance(exc, (NetOpsError, ValueError)) else HTTPStatus.INTERNAL_SERVER_ERROR
                self._send_json({"error": str(exc)}, status=status)

        return NetOpsGuiRequestHandler

    def _workspace(self) -> JsonDict:
        backend = self.backend()
        overview = backend.get_overview()
        interactions: dict[str, JsonDict] = {}
        signals: dict[str, JsonDict] = {}
        opportunities: dict[str, JsonDict] = {}
        relationships: dict[str, JsonDict] = {}
        contacts: dict[str, JsonDict] = {}

        for person in overview["people"]:
            try:
                dossier = backend.get_dossier(person["person_id"])
            except NetOpsError:
                continue
            for item in dossier["folder_payloads"]["interactions"]:
                interactions[item["id"]] = item
            for item in dossier["folder_payloads"]["signals"]:
                signals[item["id"]] = item
            for item in dossier["folder_payloads"]["opportunities"]:
                opportunities[item["id"]] = item
            for item in dossier["folder_payloads"]["connections"]:
                relationships[item["id"]] = item
            for item in dossier["folder_payloads"]["contacts"]:
                contacts[item["contact_method_id"]] = item

        return {
            "overview": overview,
            "interactions": list(interactions.values()),
            "signals": list(signals.values()),
            "opportunities": list(opportunities.values()),
            "relationships": list(relationships.values()),
            "contacts": list(contacts.values()),
        }


def launch_gui(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    desktop: bool = True,
    open_browser: bool = False,
) -> None:
    server = NetOpsGuiServer(host=host, port=port)
    if desktop:
        try:
            import webview
        except ImportError as exc:
            server.stop()
            raise RuntimeError("The desktop GUI requires pywebview. Install the GUI/portable dependencies and rebuild.") from exc

        server.start_background()
        try:
            webview.create_window(
                "NetworkOps",
                server.url,
                width=1440,
                height=900,
                min_size=(1024, 680),
                background_color="#050505",
            )
            webview.start(gui="edgechromium", debug=False)
        finally:
            server.stop()
    elif open_browser:
        server.start_background()
        webbrowser.open(server.url)
        print(f"NetworkOps GUI running at {server.url}")
        print("Close this window or press Ctrl+C to stop the local app server.")
        try:
            while True:
                threading.Event().wait(3600)
        except KeyboardInterrupt:
            server.stop()
    else:
        print(f"NetworkOps GUI running at {server.url}")
        server.serve_forever()


def _first_query(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key) or []
    return values[0] if values else None


def _path_part(path: str, index: int) -> str:
    parts = [part for part in path.split("/") if part]
    try:
        return unquote(parts[index])
    except IndexError as exc:
        raise ValueError("Missing path value.") from exc
