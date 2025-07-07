from __future__ import annotations

"""Generate CI overview HTML page."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

import tools.gen_agent_stats as gen_stats

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "ci_overview.html.j2"
STATUS_FILE = ROOT_DIR / "pipeline_status.json"


def _load_features(status_path: Path = STATUS_FILE) -> List[Dict[str, Any]]:
    features: List[Dict[str, Any]] = []
    if status_path.exists():
        try:
            data = json.loads(status_path.read_text(encoding="utf-8"))
            for name, info in data.get("features", {}).items():
                features.append(
                    {
                        "name": name,
                        "status": info.get("status"),
                        "started": info.get("started"),
                        "ended": info.get("ended"),
                        "summary": info.get("summary_path"),
                    }
                )
        except Exception:
            pass
    return features


def _pipeline_times(features: List[Dict[str, Any]]) -> tuple[str | None, str | None]:
    starts = [f.get("started") for f in features if f.get("started")]
    ends = [f.get("ended") for f in features if f.get("ended")]
    start = min(starts) if starts else None
    end = max(ends) if ends else None
    if isinstance(start, float):
        start = datetime.fromtimestamp(start).isoformat()
    if isinstance(end, float):
        end = datetime.fromtimestamp(end).isoformat()
    return start, end


def _collect_agent_stats(
    journal: Path | None = None,
    memory: Path | None = None,
    trace: Path | None = None,
) -> List[Dict[str, Any]]:
    journal = journal or gen_stats.JOURNAL_PATH
    memory = memory or gen_stats.MEMORY_PATH
    trace = trace or gen_stats.TRACE_PATH
    calls = gen_stats._parse_journal(journal)
    success, fail, autofix = gen_stats._parse_memory(memory)
    avg_time = gen_stats._parse_trace(trace)
    agents = sorted(set(calls) | set(success) | set(fail) | set(autofix) | set(avg_time))
    stats = [
        {
            "agent": a,
            "calls": calls.get(a, 0),
            "auto_fixes": autofix.get(a, 0),
            "success": success.get(a, 0),
            "fail": fail.get(a, 0),
            "avg_time": avg_time.get(a),
        }
        for a in agents
    ]
    return stats


def _list_reports(reports_dir: Path) -> List[str]:
    links: List[str] = []
    if reports_dir.exists():
        for p in sorted(reports_dir.rglob("*")):
            if p.suffix in {".html", ".md"}:
                links.append(p.relative_to(reports_dir).as_posix())
    return links


def generate_ci_overview(out_dir: str = "ci_reports") -> Path:
    """Create ci_overview.html in given directory."""
    reports_dir = Path(out_dir)
    features = _load_features()
    start, end = _pipeline_times(features)
    stats = _collect_agent_stats(
        journal=gen_stats.JOURNAL_PATH,
        memory=gen_stats.MEMORY_PATH,
        trace=gen_stats.TRACE_PATH,
    )
    links = _list_reports(reports_dir)
    metadata = {
        "start": start,
        "end": end,
        "generated": datetime.utcnow().isoformat(),
    }
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    monitor_port = os.getenv("MONITOR_PORT", "8002")
    monitor_url = os.getenv("CI_STATUS_URL", f"http://localhost:{monitor_port}/ci-status")
    html = template.render(stats=stats, reports=links, metadata=metadata, monitor_url=monitor_url)
    reports_dir.mkdir(exist_ok=True)
    out_path = reports_dir / "ci_overview.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    path = generate_ci_overview()
    print(path)
