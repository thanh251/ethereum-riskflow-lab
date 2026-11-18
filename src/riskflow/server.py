from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

from .config import PROCESSED_DIR, PROJECT_ROOT, Settings
from .storage import read_json


DASHBOARD_DIR = PROJECT_ROOT / "dashboard"


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        route = urlparse(self.path).path
        mapping = {
            "/api/graph": PROCESSED_DIR / "graph.json",
            "/api/alerts": PROCESSED_DIR / "alerts.json",
            "/api/metrics": PROCESSED_DIR / "metrics.json",
            "/api/scenario": PROCESSED_DIR / "scenario.json",
            "/api/source": PROCESSED_DIR / "source.json",
        }
        if route in mapping:
            payload = read_json(mapping[route], {} if route != "/api/alerts" else [])
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if route == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, format: str, *args) -> None:
        print(f"[dashboard] {format % args}")


def serve(host: str | None = None, port: int | None = None) -> None:
    settings = Settings.from_env()
    address = (host or settings.dashboard_host, port or settings.dashboard_port)
    server = ThreadingHTTPServer(address, DashboardHandler)
    print(f"RiskFlow dashboard: http://{address[0]}:{address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

