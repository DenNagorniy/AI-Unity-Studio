"""Simple webhook server to trigger CI pipeline."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv

from utils.agent_journal import log_action

load_dotenv()

TOKEN = os.getenv("WEBHOOK_TOKEN", "")
PORT = int(os.getenv("WEBHOOK_PORT", "8001"))
STATUS_FILE = Path("pipeline_status.json")
PROCESS: subprocess.Popen | None = None
LOCK = threading.Lock()


def _write_status(status: str) -> None:
    data = {"status": status}
    if PROCESS:
        data["pid"] = PROCESS.pid
    STATUS_FILE.write_text(json.dumps(data), encoding="utf-8")


def _run_pipeline() -> None:
    global PROCESS
    with LOCK:
        if PROCESS and PROCESS.poll() is None:
            return
        PROCESS = subprocess.Popen([sys.executable, "run_all.py"])
        _write_status("running")
        log_action("Webhook", "pipeline started")

    def wait_proc() -> None:
        assert PROCESS is not None
        ret = PROCESS.wait()
        status = "success" if ret == 0 else "error"
        with LOCK:
            _write_status(status)
        log_action("Webhook", f"pipeline {status}")

    threading.Thread(target=wait_proc, daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: D401
        if self.path != "/trigger":
            self.send_response(404)
            self.end_headers()
            return
        token = self.headers.get("X-Token")
        if TOKEN and token != TOKEN:
            self.send_response(403)
            self.end_headers()
            return
        with LOCK:
            if PROCESS and PROCESS.poll() is None:
                self.send_response(409)
                self.end_headers()
                return
        _run_pipeline()
        self.send_response(204)
        self.end_headers()


def run(server_address: tuple[str, int] = ("", PORT)) -> None:
    httpd = HTTPServer(server_address, Handler)
    print(
        f"CI webhook listening on http://{server_address[0] or 'localhost'}:{server_address[1]}/trigger"
    )
    httpd.serve_forever()


if __name__ == "__main__":
    run()
