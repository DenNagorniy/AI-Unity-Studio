from __future__ import annotations

"""Generate agent analytics HTML report."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "agent_stats.html.j2"
JOURNAL_PATH = ROOT_DIR / "agent_journal.log"
MEMORY_PATH = ROOT_DIR / "agent_memory.json"
TRACE_PATH = ROOT_DIR / "agent_trace.log"


def _parse_journal(path: Path = JOURNAL_PATH) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    if not path.exists():
        return counts
    for line in path.read_text(encoding="utf-8").splitlines():
        if "[" in line and "]" in line:
            agent = line.split("[", 1)[1].split("]", 1)[0]
            counts[agent] = counts.get(agent, 0) + 1
    return counts


def _parse_memory(path: Path = MEMORY_PATH) -> tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    success: Dict[str, int] = {}
    fail: Dict[str, int] = {}
    autofix: Dict[str, int] = {}
    if not path.exists():
        return success, fail, autofix
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        log = data.get("learning_log", {})
    except Exception:
        return success, fail, autofix
    for agent, entries in log.items():
        if agent.startswith("AutoFix:"):
            base = agent.split("AutoFix:", 1)[1]
            autofix[base] = len([e for e in entries if e.get("result") == "success"])
            continue
        s_cnt = sum(1 for e in entries if e.get("result") == "success")
        f_cnt = sum(1 for e in entries if e.get("result") != "success")
        success[agent] = s_cnt
        fail[agent] = f_cnt
    return success, fail, autofix


def _parse_trace(path: Path = TRACE_PATH) -> Dict[str, float]:
    durations: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    if not path.exists():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        agent = item.get("agent")
        start = item.get("start_time")
        end = item.get("end_time")
        if not agent or not start or not end:
            continue
        try:
            s_dt = datetime.fromisoformat(start)
            e_dt = datetime.fromisoformat(end)
        except Exception:
            continue
        dur = (e_dt - s_dt).total_seconds()
        durations[agent] = durations.get(agent, 0.0) + dur
        counts[agent] = counts.get(agent, 0) + 1
    return {a: round(durations[a] / counts[a], 2) for a in durations}


def _render(stats: List[Dict[str, Any]], metadata: Dict[str, str]) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    return template.render(stats=stats, metadata=metadata)


def generate_agent_stats(
    out_dir: str = "ci_reports",
    journal_path: Path = JOURNAL_PATH,
    memory_path: Path = MEMORY_PATH,
    trace_path: Path = TRACE_PATH,
) -> Path:
    """Generate agent_stats.html in given directory."""
    calls = _parse_journal(journal_path)
    success, fail, autofix = _parse_memory(memory_path)
    avg_time = _parse_trace(trace_path)
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
    metadata = {
        "date": datetime.utcnow().isoformat(),
        "user": os.getenv("USER", "unknown"),
    }
    html = _render(stats, metadata)
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "agent_stats.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    path = generate_agent_stats()
    print(path)


if __name__ == "__main__":
    main()
