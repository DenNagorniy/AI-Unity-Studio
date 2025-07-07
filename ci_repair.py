from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

import yaml

from utils.agent_journal import (
    LOG_PATH as JOURNAL_PATH_DEFAULT,
    TRACE_PATH as TRACE_PATH_DEFAULT,
    log_action,
)

MEMORY_PATH = Path("agent_memory.json")
CONFIG_PATH = Path("pipeline_config.yaml")
REPORTS_DIR = Path("ci_reports")

JOURNAL_PATH = JOURNAL_PATH_DEFAULT
TRACE_PATH = TRACE_PATH_DEFAULT


def _extract_agent(line: str) -> str | None:
    if "[" in line and "]" in line:
        return line.split("[", 1)[1].split("]", 1)[0]
    return None


def _load_last_errors(path: Path = JOURNAL_PATH, count: int = 3) -> List[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = [
        line
        for line in lines
        if "error" in line.lower() or "failed" in line.lower()
    ]
    return errors[-count:]


def _load_memory(path: Path = MEMORY_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _analyze_agent(agent: str, memory: dict) -> str:
    log = memory.get("learning_log", {}).get(agent, [])
    recent = log[-3:]
    results = [e.get("result") for e in recent]
    if len(recent) >= 3 and all(r != "success" for r in results):
        return "repeated_error"
    if {"success", "error"}.issubset(set(results)):
        return "unstable"
    return ""


def _collect_info() -> Tuple[List[str], List[str], List[str]]:
    last_errors = _load_last_errors()
    memory = _load_memory()
    agents = []
    reasons: List[str] = []
    suggestions: List[str] = []
    for line in last_errors:
        agent = _extract_agent(line)
        if not agent:
            continue
        if agent not in agents:
            agents.append(agent)
        status = _analyze_agent(agent, memory)
        if status == "repeated_error":
            reasons.append(f"- {agent}: 3 ошибки подряд")
            suggestions.append(f"- Перезапустить {agent} в изоляции")
        elif status == "unstable":
            reasons.append(f"- {agent}: нестабильный вывод")
        else:
            reasons.append(f"- {agent}: ошибка")
    if agents:
        suggestions.append("- Пропустить RefactorAgent")
        suggestions.append("- Проверить TeamLead патч")
    return agents, reasons, suggestions


def _save_report(
    reasons: List[str],
    suggestions: List[str],
    out_dir: Path = REPORTS_DIR,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# 🛠 Repair Suggestions", "", "## Причины:"]
    lines += reasons or ["- нет данных"]
    lines += ["", "## Предлагается:"]
    lines += suggestions or ["- нет действий"]
    out_path = out_dir / "repair_suggestion.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def _update_config(skip_agents: List[str], path: Path = CONFIG_PATH) -> None:
    if not path.exists() or not skip_agents:
        return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", [])
    if not isinstance(agents, list):
        return
    new_agents = [a for a in agents if a not in skip_agents]
    data["agents"] = new_agents
    dumped = yaml.safe_dump(data, sort_keys=False)
    path.write_text(dumped, encoding="utf-8")


def main(feature: str | None = None, auto_repair: bool = False) -> Path:
    agents, reasons, suggestions = _collect_info()
    report = _save_report(reasons, suggestions)
    log_action("CIRepair", f"suggestions for {feature or 'unknown'}")
    if auto_repair:
        _update_config(agents)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CI Repair Agent")
    parser.add_argument("--feature", help="Feature name", default=None)
    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="Modify pipeline config",
    )
    args = parser.parse_args()
    result = main(feature=args.feature, auto_repair=args.auto_repair)
    print(result)
