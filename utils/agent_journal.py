from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, List

LOG_PATH = Path("agent_journal.log")
TRACE_PATH = Path("agent_trace.log")


def log_action(agent: str, action: str) -> None:
    timestamp = datetime.utcnow().isoformat()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} [{agent}] {action}\n")


def read_entries() -> List[str]:
    if not LOG_PATH.exists():
        return []
    return LOG_PATH.read_text(encoding="utf-8").splitlines()


def log_trace(agent: str, stage: str, data_in: Any, data_out: Any) -> None:
    """Write detailed trace of agent interactions."""
    TRACE_PATH.parent.mkdir(exist_ok=True, parents=True)
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "time": timestamp,
        "agent": agent,
        "stage": stage,
        "input": data_in,
        "output": data_out,
    }
    with TRACE_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{json.dumps(entry, ensure_ascii=False)}\n")

