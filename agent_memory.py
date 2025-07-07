import json
from pathlib import Path
from typing import Any, Dict

from utils.agent_journal import log_action

MEMORY_PATH = Path("agent_memory.json")
_enabled = False
_data: Dict[str, Any] = {}


def enable() -> None:
    """Enable shared memory and load existing data."""
    global _enabled, _data
    _enabled = True
    if MEMORY_PATH.exists():
        try:
            _data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            _data = {}
    log_action("Memory", "enabled")


def _save() -> None:
    MEMORY_PATH.write_text(
        json.dumps(_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write(key: str, value: Any) -> None:
    """Store a JSON-serializable value under key."""
    if not _enabled:
        return
    _data[key] = value
    _save()
    log_action("Memory", f"write {key}")


def read(key: str) -> Any:
    """Read value from memory."""
    if not _enabled:
        return None
    log_action("Memory", f"read {key}")
    return _data.get(key)
