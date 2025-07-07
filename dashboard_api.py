from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.agent_journal import read_entries
from utils.feature_index import load_index


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: D401
        if self.path != "/data":
            self.send_response(404)
            self.end_headers()
            return
        review_data = {}
        try:
            with open("review_report.json", "r", encoding="utf-8") as f:
                review_data = json.load(f)
        except FileNotFoundError:
            pass

        data = {
            "index": load_index(),
            "journal": read_entries(),
            "review": review_data,
        }
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
