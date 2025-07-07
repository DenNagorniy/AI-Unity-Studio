from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

from agents.tech import team_lead
from utils.agent_journal import log_action

TEMPLATE_DIR = Path("templates")
TEMPLATE_NAME = "autofailure_report.md.j2"


def detect_repeated_failures(memory_path: Path = Path("agent_memory.json"), threshold: int = 3) -> List[Dict[str, Any]]:
    """Return info about agents with repeated errors for the same input."""
    if not memory_path.exists():
        return []
    try:
        data = json.loads(memory_path.read_text(encoding="utf-8"))
        log = data.get("learning_log", {})
    except Exception:
        return []

    failures: List[Dict[str, Any]] = []
    for agent, entries in log.items():
        if agent.startswith("AutoFix:"):
            continue
        last_hash = None
        count = 0
        last_exc = ""
        for item in reversed(entries):
            if item.get("result") != "error":
                break
            h = item.get("hash")
            if last_hash is None:
                last_hash = h
            if h != last_hash:
                break
            count += 1
            last_exc = str(item.get("output", ""))
        if count > threshold:
            failures.append(
                {
                    "agent": agent,
                    "stage": agent.replace("Agent", ""),
                    "count": count,
                    "exception": last_exc,
                }
            )
    return failures


def trigger_teamlead_analysis(failures: List[Dict[str, Any]]) -> str:
    """Notify TeamLeadAgent and return recommendation string."""
    if not failures:
        return ""
    summary = "; ".join(f"{f['agent']} {f['count']}x" for f in failures)
    team_lead.log(f"Auto escalation triggered: {summary}")
    log_action("TeamLead", f"escalation {summary}")
    return "TeamLead notified. Investigate failing agents."


def generate_report(failures: List[Dict[str, Any]], recommendations: str, out_dir: str = "ci_reports") -> Path:
    """Render markdown report with failure details."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    content = template.render(failures=failures, recommendations=recommendations)
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "autofailure_report.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main(out_dir: str = "ci_reports") -> Path | None:
    """Run detection, analysis and report generation."""
    failures = detect_repeated_failures()
    if not failures:
        return None
    rec = trigger_teamlead_analysis(failures)
    return generate_report(failures, rec, out_dir)


if __name__ == "__main__":
    result = main()
    if result:
        print(result)
