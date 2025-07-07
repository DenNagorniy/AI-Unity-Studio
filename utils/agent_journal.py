from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

LOG_PATH = Path("agent_journal.log")


def log_action(agent: str, action: str) -> None:
    timestamp = datetime.utcnow().isoformat()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} [{agent}] {action}\n")


def read_entries() -> List[str]:
    if not LOG_PATH.exists():
        return []
    return LOG_PATH.read_text(encoding="utf-8").splitlines()
