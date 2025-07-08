from __future__ import annotations

"""Generate agent scoring report based on pipeline logs."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "agent_scores.html.j2"
JOURNAL_PATH = ROOT_DIR / "agent_journal.log"
MEMORY_PATH = ROOT_DIR / "agent_memory.json"
TRACE_PATH = ROOT_DIR / "agent_trace.log"
SCORES_JSON = ROOT_DIR / "agent_scores.json"

AGENT_RE = re.compile(r"([A-Za-z]+Agent)")


def _parse_journal(path: Path = JOURNAL_PATH) -> tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    calls: Dict[str, int] = {}
    escalations: Dict[str, int] = {}
    self_improve: Dict[str, int] = {}
    if not path.exists():
        return calls, escalations, self_improve
    for line in path.read_text(encoding="utf-8").splitlines():
        if "| AUTO_FIX |" in line:
            parts = line.split("|")
            if len(parts) > 2:
                ag = parts[2].strip()
                calls.setdefault(ag, 0)
            continue
        if "[" in line and "]" in line:
            ag = line.split("[", 1)[1].split("]", 1)[0]
            calls[ag] = calls.get(ag, 0) + 1
            if ag == "SelfImproverAgent":
                for m in AGENT_RE.findall(line):
                    if m != "SelfImproverAgent":
                        self_improve[m] = self_improve.get(m, 0) + 1
        if "escalation" in line:
            for m in AGENT_RE.findall(line):
                if m not in {"TeamLead", "TeamLeadAgent"}:
                    escalations[m] = escalations.get(m, 0) + 1
    return calls, escalations, self_improve


def _calc_trend(entries: List[dict]) -> str:
    recent = entries[-5:]
    prev = entries[-10:-5]

    def _rate(items: List[dict]) -> float:
        if not items:
            return 0.0
        return sum(1 for e in items if e.get("result") == "success") / len(items)

    if not prev:
        return "n/a"
    r_recent = _rate(recent)
    r_prev = _rate(prev)
    if r_recent > r_prev:
        return "up"
    if r_recent < r_prev:
        return "down"
    return "same"


def _parse_memory(path: Path = MEMORY_PATH) -> tuple[Dict[str, int], Dict[str, int], Dict[str, int], Dict[str, str]]:
    success: Dict[str, int] = {}
    fail: Dict[str, int] = {}
    autofix: Dict[str, int] = {}
    trend: Dict[str, str] = {}
    if not path.exists():
        return success, fail, autofix, trend
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        log = data.get("learning_log", {})
    except Exception:
        return success, fail, autofix, trend
    for agent, entries in log.items():
        if agent.startswith("AutoFix:"):
            base = agent.split("AutoFix:", 1)[1]
            autofix[base] = len(entries)
            continue
        success_count = sum(1 for e in entries if e.get("result") == "success")
        success[agent] = success_count
        fail[agent] = len(entries) - success_count
        trend[agent] = _calc_trend(entries)
    return success, fail, autofix, trend


def _render(scores: List[Dict[str, Any]], generated: str) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    return template.render(scores=scores, generated=generated)


def generate_agent_scores(
    out_dir: str = "ci_reports",
    journal_path: Path = JOURNAL_PATH,
    memory_path: Path = MEMORY_PATH,
    trace_path: Path = TRACE_PATH,
    scores_path: Path = SCORES_JSON,
) -> Path:
    """Generate agent_scores.html and update agent_scores.json."""
    calls, escalations, self_improve = _parse_journal(journal_path)
    success, fail, autofix_mem, trend = _parse_memory(memory_path)
    autofix = {**autofix_mem}
    agents = sorted(set(calls) | set(success) | set(fail) | set(autofix) | set(escalations) | set(self_improve))
    scores: List[Dict[str, Any]] = []
    json_data: Dict[str, Any] = {}
    for ag in agents:
        s = success.get(ag, 0)
        f = fail.get(ag, 0)
        total = s + f
        rate = s / total if total else 0.0
        info = {
            "agent": ag,
            "calls": calls.get(ag, 0),
            "success": s,
            "fail": f,
            "autofix": autofix.get(ag, 0),
            "escalations": escalations.get(ag, 0),
            "self_improve": self_improve.get(ag, 0),
            "success_rate": round(rate, 2) if total else None,
            "trend": trend.get(ag, "n/a"),
        }
        scores.append(info)
        json_data[ag] = info
    scores_path.write_text(json.dumps(json_data, ensure_ascii=False), encoding="utf-8")
    html = _render(scores, datetime.utcnow().isoformat())
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "agent_scores.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    path = generate_agent_scores()
    print(path)


if __name__ == "__main__":
    main()
