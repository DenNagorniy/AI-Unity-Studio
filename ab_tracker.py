from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict

from utils.agent_journal import log_action, log_trace

PROJECT_MAP = Path("project_map.json")
RESULTS_FILE = Path("ab_test_results.json")
REPORT_FILE = Path("ab_test_report.md")


def _load_project_map(path: Path = PROJECT_MAP) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _collect_events(feature: str, variants: list[str]) -> Dict[str, Dict[str, int]]:
    """Return mocked events for each variant."""
    events: Dict[str, Dict[str, int]] = {}
    for v in variants:
        events[v] = {
            "feature_used": random.randint(50, 100),
            "step_completed": random.randint(10, 50),
            "error_occured": random.randint(0, 5),
        }
    return events


def _write_report(
    data: Dict[str, Dict[str, Dict[str, int]]], winners: Dict[str, str], path: Path
) -> None:
    lines = ["# A/B Test Report", ""]
    for feat, variants in data.items():
        lines.append(f"## {feat}")
        lines.append("| Variant | feature_used | step_completed | error_occured |")
        lines.append("|---------|--------------|----------------|---------------|")
        for variant, metrics in variants.items():
            lines.append(
                f"| {variant} | {metrics['feature_used']} | {metrics['step_completed']} | {metrics['error_occured']} |"
            )
        lines.append("")
        lines.append(f"**Winner:** {winners.get(feat, '-')}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run(data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run A/B tracker and generate report."""
    data = data or {}
    out_dir = Path(data.get("out_dir", "."))
    log_action("ABTrackerAgent", "start")

    pm = _load_project_map()
    ab_tests: Dict[str, Dict[str, Dict[str, int]]] = {}
    for fname, info in pm.get("features", {}).items():
        variants = info.get("variants")
        if variants:
            ab_tests[fname] = _collect_events(fname, list(variants))

    if not ab_tests:
        result = {"status": "no_tests"}
        log_trace("ABTrackerAgent", "run", data, result)
        return result

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / RESULTS_FILE.name).write_text(
        json.dumps(ab_tests, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    winners: Dict[str, str] = {}
    for feat, variants in ab_tests.items():
        winner = max(variants.items(), key=lambda kv: kv[1]["step_completed"])[0]
        winners[feat] = winner

    report_path = out_dir / REPORT_FILE.name
    _write_report(ab_tests, winners, report_path)

    result = {"status": "success", "winners": winners, "report": str(report_path)}
    log_trace("ABTrackerAgent", "run", data, result)
    return result


if __name__ == "__main__":
    print(run())
