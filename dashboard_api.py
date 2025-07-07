from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from utils.agent_journal import read_entries
from utils.feature_index import load_index


def _load_learning_stats() -> dict:
    path = Path("agent_memory.json")
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        log = data.get("learning_log", {})
    except Exception:
        return {}

    stats: dict[str, dict] = {}
    for agent, entries in log.items():
        if agent.startswith("AutoFix:"):
            continue
        total = len(entries)
        successful = sum(1 for e in entries if e.get("result") == "success")
        examples = [e.get("input", "") for e in entries[:3]]
        auto_entries = log.get(f"AutoFix:{agent}", [])
        auto_patterns = {
            e.get("output")
            for e in auto_entries
            if e.get("result") == "success" and e.get("output")
        }
        stats[agent] = {
            "total_calls": total,
            "successful": successful,
            "auto_fixes": len(auto_patterns),
            "examples": examples,
        }
    return stats


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: D401
        if self.path == "/data":
            self._send_json(self._collect_data())
        elif self.path == "/learning":
            self._send_json(_load_learning_stats())
        else:
            self.send_response(404)
            self.end_headers()

    def _collect_data(self) -> dict:
        review_data = {}
        try:
            with open("review_report.json", "r", encoding="utf-8") as f:
                review_data = json.load(f)
        except FileNotFoundError:
            pass

        return {
            "index": load_index(),
            "journal": read_entries(),
            "review": review_data,
        }

    def _send_json(self, data: dict) -> None:
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(server_address: tuple[str, int] = ("", 8000)) -> None:
    httpd = HTTPServer(server_address, Handler)
    print(f"📊 Dashboard API running on http://{server_address[0] or 'localhost'}:{server_address[1]}/data")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
