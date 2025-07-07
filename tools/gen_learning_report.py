"""Generate HTML report summarizing agent learning."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "learning_report.html.j2"
MEMORY_PATH = ROOT_DIR / "agent_memory.json"


def _load_log(memory_path: Path = MEMORY_PATH) -> Dict[str, List[dict]]:
    if memory_path.exists():
        try:
            data = json.loads(memory_path.read_text(encoding="utf-8"))
            return data.get("learning_log", {})
        except Exception:
            return {}
    return {}


def _collect_stats(log: Dict[str, List[dict]]) -> List[Dict[str, Any]]:
    stats: List[Dict[str, Any]] = []
    for agent in sorted(k for k in log if not k.startswith("AutoFix:")):
        entries = log.get(agent, [])
        success_entries = [e for e in entries if e.get("result") == "success"]
        unique_hashes = {e.get("hash") for e in success_entries}
        examples = [
            {
                "input": e.get("input", "")[:80],
                "hint": e.get("output", "")[:80],
            }
            for e in success_entries[:3]
        ]
        autofix = log.get(f"AutoFix:{agent}", [])
        patterns = {
            e.get("output")
            for e in autofix
            if e.get("result") == "success" and e.get("output")
        }
        stats.append(
            {
                "agent": agent,
                "unique_success": len(unique_hashes),
                "examples": examples,
                "auto_fix": len(patterns),
            }
        )
    return stats


def _render(stats: List[Dict[str, Any]], metadata: Dict[str, str]) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    return template.render(stats=stats, metadata=metadata)


def generate_learning_report(
    out_dir: str = "ci_reports", memory_path: Path = MEMORY_PATH
) -> Path:
    """Generate learning_report.html in given directory."""
    log = _load_log(memory_path)
    stats = _collect_stats(log)
    metadata = {
        "date": datetime.utcnow().isoformat(),
        "user": os.getenv("USER", "unknown"),
    }
    html = _render(stats, metadata)
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "learning_report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    path = generate_learning_report()
    print(path)


if __name__ == "__main__":
    main()
