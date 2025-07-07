from __future__ import annotations

"""Generate HTML trace report from agent_trace.log."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "trace_report.html.j2"
TRACE_LOG = ROOT_DIR / "agent_trace.log"


def _load_entries(log_path: Path = TRACE_LOG) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    if not log_path.exists():
        return entries
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries


def _compute_stats(entries: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    by_agent: Dict[str, List[float]] = {}
    timeline: List[Dict[str, Any]] = []
    for item in entries:
        agent = item.get("agent")
        start = item.get("start_time")
        end = item.get("end_time")
        status = item.get("status", "")
        if not agent or not start or not end:
            continue
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
        except Exception:
            continue
        duration = (end_dt - start_dt).total_seconds()
        by_agent.setdefault(agent, []).append(duration)
        timeline.append(
            {
                "agent": agent,
                "start": start_dt.isoformat(),
                "duration": round(duration, 2),
                "status": status,
            }
        )
    stats = [
        {
            "agent": agent,
            "total": round(sum(durations), 2),
            "avg": round(sum(durations) / len(durations), 2),
            "count": len(durations),
        }
        for agent, durations in by_agent.items()
    ]
    stats.sort(key=lambda x: x["total"], reverse=True)
    timeline.sort(key=lambda x: x["start"])
    return stats, timeline


def _recommend_flags(entries: List[Dict[str, Any]]) -> List[str]:
    by_agent: Dict[str, List[str]] = {}
    for item in entries:
        agent = item.get("agent")
        status = item.get("status", "")
        if agent:
            by_agent.setdefault(agent, []).append(status)
    flags: List[str] = []
    for agent, statuses in by_agent.items():
        if statuses and all(s == "success" for s in statuses) and len(statuses) > 1:
            name = agent.replace("Agent", "").lower()
            flags.append(f"--skip={name}")
    return flags


def _render(
    stats: List[Dict[str, Any]],
    timeline: List[Dict[str, Any]],
    flags: List[str],
    metadata: Dict[str, str],
) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    return template.render(stats=stats, timeline=timeline, flags=flags, metadata=metadata)


def generate_trace_report(out_dir: str = "ci_reports", log_path: Path = TRACE_LOG) -> Path:
    entries = _load_entries(log_path)
    stats, timeline = _compute_stats(entries)
    flags = _recommend_flags(entries)
    metadata = {
        "date": datetime.utcnow().isoformat(),
        "user": os.getenv("USER", "unknown"),
    }
    html = _render(stats, timeline, flags, metadata)
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "trace_report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    path = generate_trace_report()
    print(path)


if __name__ == "__main__":
    main()
