"""Generate HTML QC report for assets."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader
from utils.asset_qc import (
    _check_texture,
    _count_obj_polygons,
    MAX_TEXTURE_RESOLUTION,
)

TEMPLATE_DIR = Path("templates")
TEMPLATE_NAME = "assets_report.html.j2"
QC_JSON = Path("asset_qc.json")


def _load_issues() -> Dict[str, List[str]]:
    issues: Dict[str, List[str]] = {}
    if not QC_JSON.exists():
        return issues
    data = json.loads(QC_JSON.read_text(encoding="utf-8"))
    for item in data:
        asset = item.get("asset", "")
        issue = item.get("issue", "")
        issues.setdefault(asset, []).append(issue)
    return issues


def _render(assets: List[Dict[str, str]], metadata: Dict[str, str]) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    return template.render(assets=assets, metadata=metadata)


def generate_assets_report(
    asset_dir: str = "Assets",
    out_dir: str = "ci_reports",
) -> Path:
    """Create assets_report.html summarizing QC results."""
    issue_map = _load_issues()
    entries: List[Dict[str, str]] = []
    for root, _dirs, files in os.walk(asset_dir):
        for name in files:
            path = Path(root) / name
            rel_path = path.as_posix()
            ext = path.suffix.lower()
            polygons = "-"
            texture = "-"
            if ext == ".obj":
                polygons = str(_count_obj_polygons(path))
            elif ext in {".png", ".jpg", ".jpeg"}:
                _ok, w, h = _check_texture(path, MAX_TEXTURE_RESOLUTION)
                texture = f"{w}x{h}"
            status = "OK" if rel_path not in issue_map else "Error"
            entries.append(
                {
                    "name": name,
                    "path": rel_path,
                    "polygons": polygons,
                    "texture": texture,
                    "status": status,
                }
            )
    metadata = {
        "date": datetime.utcnow().isoformat(),
        "git_commit": subprocess.check_output([
            "git",
            "rev-parse",
            "HEAD",
        ]).decode().strip(),
        "user": os.getenv("USER", "unknown"),
    }
    html = _render(entries, metadata)
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "assets_report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    path = generate_assets_report()
    print(path)


if __name__ == "__main__":
    main()
