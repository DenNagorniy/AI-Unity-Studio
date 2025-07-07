from __future__ import annotations

"""SelfImproverAgent adjusts pipeline config based on analytics."""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from utils.agent_journal import log_action, log_trace

CONFIG_PATH = Path("pipeline_config.yaml")
BACKUP_PATH = Path("pipeline_config.backup.yaml")


def _parse_commands(text: str) -> Dict[str, List[str]]:
    skip: List[str] = []
    prioritize: List[str] = []
    reasons: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        upper = stripped.upper()
        if upper.startswith("SKIP "):
            agent = stripped.split()[1]
            skip.append(agent)
            reasons.append(stripped)
        elif upper.startswith("PRIORITIZE "):
            agent = stripped.split()[1]
            prioritize.append(agent)
            reasons.append(stripped)
    return {"skip": skip, "prioritize": prioritize, "reasons": reasons}


def _load_insights(meta_path: Path) -> Dict[str, List[str]]:
    if not meta_path.exists():
        return {"skip": [], "prioritize": [], "reasons": []}
    try:
        text = meta_path.read_text(encoding="utf-8")
    except Exception:
        return {"skip": [], "prioritize": [], "reasons": []}
    return _parse_commands(text)


def _apply_changes(cfg: Dict[str, Any], commands: Dict[str, List[str]]) -> List[str]:
    agents = cfg.get("agents", [])
    if not isinstance(agents, list):
        return []
    changes: List[str] = []
    for ag in commands.get("skip", []):
        if ag in agents:
            agents.remove(ag)
            changes.append(f"Removed {ag}")
    for ag in commands.get("prioritize", []):
        if ag in agents:
            agents.remove(ag)
            agents.insert(0, ag)
            changes.append(f"Prioritized {ag}")
    cfg["agents"] = agents
    return changes


def _save_config(cfg: Dict[str, Any]) -> None:
    if CONFIG_PATH.exists():
        BACKUP_PATH.write_text(CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    dumped = yaml.safe_dump(cfg, sort_keys=False)
    CONFIG_PATH.write_text(dumped, encoding="utf-8")


def run(data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Execute SelfImproverAgent and produce improvement report."""
    data = data or {}
    out_dir = Path(data.get("out_dir", "."))

    log_action("SelfImproverAgent", "start")

    meta_path = Path(data.get("meta_path", out_dir / "meta_insights.md"))
    commands = _load_insights(meta_path)

    cfg: Dict[str, Any] = {}
    if CONFIG_PATH.exists():
        cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    changes = _apply_changes(cfg, commands)
    _save_config(cfg)

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "self_improvement.md"

    lines = [
        "# Self-Improvement Suggestions",
        "",
        f"Generated: {datetime.utcnow().isoformat()}",
        f"Source: {meta_path.name}",
        "",
        "## Applied Changes",
    ]
    lines += [f"- {c}" for c in changes] or ["- none"]
    lines += ["", "## Reasons"]
    lines += [f"- {r}" for r in commands.get("reasons", [])] or ["- none"]

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = {"status": "success", "report": str(report_path), "config": str(CONFIG_PATH)}
    log_trace("SelfImproverAgent", "run", data, result)
    return result


if __name__ == "__main__":
    print(run())
