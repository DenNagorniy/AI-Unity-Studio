from __future__ import annotations

import json
import threading
from http.server import HTTPServer

import requests

import ci_monitor


def _start_server() -> tuple[HTTPServer, int]:
    httpd = HTTPServer(("localhost", 0), ci_monitor.Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def test_status_and_reports(monkeypatch, tmp_path):
    status_file = tmp_path / "status.json"
    status_file.write_text(json.dumps({"status": "success"}), encoding="utf-8")
    reports_dir = tmp_path / "ci_reports"
    reports_dir.mkdir()
    (reports_dir / "build.zip").write_text("zip", encoding="utf-8")
    monkeypatch.setattr(ci_monitor, "STATUS_FILE", status_file)
    monkeypatch.setattr(ci_monitor, "REPORTS_DIR", reports_dir)

    httpd, port = _start_server()
    try:
        resp = requests.get(f"http://localhost:{port}/status", timeout=5)
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

        resp = requests.get(f"http://localhost:{port}/reports", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert any("build.zip" in p for p in data["artifacts"])
        assert data["summary"].endswith("summary.html")
    finally:
        httpd.shutdown()


def test_ci_status(monkeypatch, tmp_path):
    data = {
        "features": {
            "feat": {
                "status": "running",
                "started": 1.0,
                "ended": 2.0,
                "duration": 1.0,
                "summary_path": "feat/summary.html",
                "agent_results": {},
                "is_multi": True,
            }
        },
        "multi": True,
    }
    status_file = tmp_path / "status.json"
    status_file.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(ci_monitor, "STATUS_FILE", status_file)
    httpd, port = _start_server()
    try:
        resp = requests.get(f"http://localhost:{port}/ci-status", timeout=5)
        assert resp.status_code == 200
        info = resp.json()["features"][0]
        assert info["feature"] == "feat"
        assert info["status"] == "running"
    finally:
        httpd.shutdown()
