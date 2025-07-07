from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

CONFIG_PATH = Path("pipeline_config.yaml")

DEFAULT_CONFIG: Dict[str, Any] = {
    "steps": {"build": True, "publish": True, "qc": True},
    "agents": [],
}


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    else:
        data = {}
    cfg = {
        "steps": DEFAULT_CONFIG["steps"].copy(),
        "agents": data.get("agents", DEFAULT_CONFIG["agents"]),
    }
    if isinstance(data.get("steps"), dict):
        cfg["steps"].update({k: bool(v) for k, v in data["steps"].items()})
    return cfg
