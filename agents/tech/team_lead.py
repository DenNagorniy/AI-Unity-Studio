# agents/tech/team_lead.py
from __future__ import annotations

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


def update_project_map(feature: str, tested: bool) -> None:
    """Mark feature as tested in project_map.json."""
    _ensure_files()
    data = json.loads(PM_PATH.read_text(encoding="utf-8"))
    features = data.setdefault("features", {})
    info = features.setdefault(feature, {})
    info["tested"] = tested
    PM_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_metrics(metrics: dict) -> None:
    """Append metrics entry to metrics.json."""
    _ensure_files()
    data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    data.append({"time": datetime.utcnow().isoformat(), **metrics})
    METRICS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def merge_feature(feature: str, metrics: dict) -> None:
    """Simulate merge of a feature and record metrics."""
    log(f"Merging feature {feature}")
    update_project_map(feature, metrics.get("tests_passed", 0) > 0)
    record_metrics({"feature": feature, **metrics})
