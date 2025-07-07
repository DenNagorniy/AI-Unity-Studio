"""Simple monitoring API for CI pipeline."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("MONITOR_PORT", "8002"))
STATUS_FILE = Path("pipeline_status.json")
REPORTS_DIR = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: D401
        if self.path == "/status":
            self._send_json(self._read_status())
        elif self.path == "/reports":
            self._send_json(self._collect_reports())
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data: dict) -> None:
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_status(self) -> dict:
        if STATUS_FILE.exists():
            try:
                return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"status": "idle"}

    def _collect_reports(self) -> dict:
        artifacts: list[str] = []
        if REPORTS_DIR.exists():
            for p in REPORTS_DIR.iterdir():
                if p.suffix in {".zip", ".apk"}:
                    artifacts.append(str(p))
        summary = str(REPORTS_DIR / "summary.html") if (REPORTS_DIR / "summary.html").exists() else ""
        changelog = str(Path("CHANGELOG.md")) if Path("CHANGELOG.md").exists() else ""
        return {"artifacts": artifacts, "summary": summary, "changelog": changelog}


def run(server_address: tuple[str, int] = ("", PORT)) -> None:
    httpd = HTTPServer(server_address, Handler)
    print(
        f"CI monitor running on http://{server_address[0] or 'localhost'}:{server_address[1]}"
    )
    httpd.serve_forever()


if __name__ == "__main__":
    run()
