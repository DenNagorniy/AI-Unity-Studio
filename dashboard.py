from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Environment, FileSystemLoader


def main() -> None:
    try:
        with urlopen("http://localhost:8000/data") as resp:
            data = json.loads(resp.read().decode())
        features = {f["name"]: f for f in data.get("index", {}).get("features", [])}
        metrics = {}
    except URLError:
        features = {}
        if Path("project_map.json").exists():
            data = json.loads(Path("project_map.json").read_text(encoding="utf-8"))
            features = data.get("features", {})

        metrics = {}
        metrics_path = Path("metrics.json")
        if metrics_path.exists():
            entries = json.loads(metrics_path.read_text(encoding="utf-8"))
            if isinstance(entries, list) and entries:
                metrics = entries[-1]

    print("=== Pipeline Dashboard ===")
    if features:
        print("Features:")
        for name, feat in features.items():
            status = "✅" if feat.get("tested") else "❌"
            print(f"- {name}: {status}")
    if metrics:
        print("\nLatest metrics:")
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: D401
        if self.path == "/ci-status":
            self._send_html(self._render_ci())
        else:
            self.send_response(404)
            self.end_headers()

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _render_ci(self) -> str:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("ci_status.html.j2")
        monitor_port = os.getenv("MONITOR_PORT", "8002")
        url = f"http://localhost:{monitor_port}/ci-status"
        return template.render(monitor_url=url)


def run(server_address: tuple[str, int] = ("", 8000)) -> None:
    httpd = HTTPServer(server_address, WebHandler)
    host = server_address[0] or "localhost"
    print(f"Dashboard running on http://{host}:{server_address[1]}/ci-status")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="Run web dashboard")
    args = parser.parse_args()
    if args.serve:
        run()
    else:
        main()
