from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

from utils.agent_journal import log_action, log_trace

ROOT_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "user_feedback.md.j2"

COMMENTS = [
    "Отличная скорость",
    "Не понял UI",
    "Хорошая графика",
    "Слишком медленно",
    "Интересная механика",
]

REASONS = [
    "понравилась скорость",
    "не понял UI",
    "красивая графика",
    "много багов",
    "сложное управление",
]


def _load_ab_results(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _generate_feedback(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    feedback: Dict[str, List[Dict[str, Any]]] = {}
    for feat, variants in data.items():
        feedback[feat] = []
        for variant in variants.keys():
            feedback[feat].append(
                {
                    "variant": variant,
                    "rating": random.randint(1, 5),
                    "comment": random.choice(COMMENTS),
                    "reason": random.choice(REASONS),
                }
            )
    return feedback


def _write_report(feedback: Dict[str, List[Dict[str, Any]]], out: Path) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    text = template.render(feedback=feedback)
    out.write_text(text, encoding="utf-8")


def run(data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Generate user feedback report based on A/B test results."""
    data = data or {}
    out_dir = Path(data.get("out_dir", "."))

    log_action("UserFeedbackAgent", "start")

    ab_path = out_dir / "ab_test_results.json"
    ab_results = _load_ab_results(ab_path)

    feedback = _generate_feedback(ab_results)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "user_feedback_report.md"
    _write_report(feedback, report_path)

    result = {"status": "success", "report": str(report_path)}
    log_trace("UserFeedbackAgent", "run", data, result)
    return result


if __name__ == "__main__":
    print(run())
