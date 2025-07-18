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
        elif self.path == "/ci-status":
            self._send_json(self._read_ci_status())
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
        summary = str(REPORTS_DIR / "summary.html")
        changelog_path = Path("CHANGELOG.md")
        changelog = (
            changelog_path.read_text(encoding="utf-8")
            if changelog_path.exists()
            else ""
        )
        return {
            "artifacts": artifacts,
            "summary": summary,
            "changelog": changelog,
        }

    def _read_ci_status(self) -> dict:
        if STATUS_FILE.exists():
            try:
                data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
                features = []
                for name, info in data.get("features", {}).items():
                    features.append(
                        {
                            "feature": name,
                            "status": info.get("status"),
                            "started": info.get("started"),
                            "ended": info.get("ended"),
                            "duration": info.get("duration"),
                            "summary": info.get("summary_path"),
                            "multi": info.get("is_multi", False),
                        }
                    )
                return {"features": features}
            except Exception:
                pass
        return {"features": []}


def run(server_address: tuple[str, int] = ("", PORT)) -> None:
    httpd = HTTPServer(server_address, Handler)
    host = server_address[0] or "localhost"
    print(f"CI monitor running on http://{host}:{server_address[1]}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
