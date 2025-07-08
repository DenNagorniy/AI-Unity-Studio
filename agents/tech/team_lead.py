# agents/tech/team_lead.py
from __future__ import annotations

"""Persist metrics and logs for each pipeline execution."""

import json
from datetime import datetime
from pathlib import Path

PM_PATH = Path("project_map.json")
JOURNAL_PATH = Path("journal.json")
METRICS_PATH = Path("metrics.json")


def _ensure_files() -> None:
    if not PM_PATH.exists():
        PM_PATH.write_text('{"schema_version":1,"features":{}}', encoding="utf-8")
    if not JOURNAL_PATH.exists():
        JOURNAL_PATH.write_text("[]", encoding="utf-8")
    if not METRICS_PATH.exists():
        METRICS_PATH.write_text("[]", encoding="utf-8")


def log(msg: str) -> None:
    """Log a message and append it to journal.json."""
    _ensure_files()
    print(f"[TeamLead] {msg}", flush=True)
    data = json.loads(JOURNAL_PATH.read_text(encoding="utf-8"))
    data.append({"time": datetime.utcnow().isoformat(), "msg": msg})
    JOURNAL_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def update_project_map(feature_id: str, files: list, tested: bool):
    _ensure_files()
    with open("project_map.json", "r") as f:
        data = json.load(f)

    data["features"][feature_id] = {
        "name": feature_id,
        "status": "done" if tested else "failed",
        "files": files,
        "assets": [],
        "created_by": "CoderAgent",
        "created_at": datetime.utcnow().isoformat(),
        "tested": tested,
        "depends_on": [],
        "deleted": False,
    }

    with open("project_map.json", "w") as f:
        json.dump(data, f, indent=2)


def record_metrics(metrics: dict) -> None:
    """Append metrics entry to metrics.json."""
    _ensure_files()
    data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    data.append({"time": datetime.utcnow().isoformat(), **metrics})
    METRICS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def merge_feature(feature: str, metrics: dict) -> None:
    """Simulate merge of a feature and record metrics."""
    log(f"Merging feature {feature}")
    update_project_map(feature, [], metrics.get("tests_passed", 0) > 0)
    record_metrics({"feature": feature, **metrics})
