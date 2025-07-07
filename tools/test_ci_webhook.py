from __future__ import annotations

import json
import threading
import time
from http.server import HTTPServer

import requests

import ci_webhook


class DummyProcess:
    def __init__(self) -> None:
        self.pid = 1

    def poll(self) -> int | None:
        return None

    def wait(self) -> int:
        return 0


def _start_server() -> tuple[HTTPServer, int]:
    httpd = HTTPServer(("localhost", 0), ci_webhook.Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def test_trigger(monkeypatch, tmp_path):
    monkeypatch.setenv("WEBHOOK_TOKEN", "tok")
    monkeypatch.setattr(ci_webhook, "PROCESS", None)
    monkeypatch.setattr(ci_webhook, "STATUS_FILE", tmp_path / "status.json")

    def fake_popen(args, **kwargs):  # noqa: ANN001
        return DummyProcess()

    monkeypatch.setattr(ci_webhook.subprocess, "Popen", fake_popen)

    httpd, port = _start_server()
    try:
        resp = requests.post(f"http://localhost:{port}/trigger", headers={"X-Token": "tok"}, timeout=5)
        assert resp.status_code == 204
        time.sleep(0.1)
        data = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
        assert data["status"] == "success"
    finally:
        httpd.shutdown()
