"""Simple agent learning mechanism based on previous interactions."""

from __future__ import annotations

import difflib
import hashlib
import json
from typing import Any, Dict, List

import agent_memory
from utils.agent_journal import log_action

_LOG_KEY = "learning_log"


def _load_log() -> Dict[str, List[dict]]:
    log = agent_memory.read(_LOG_KEY)
    if log is None:
        log = {}
        agent_memory.write(_LOG_KEY, log)
    return log


def _save_log(log: Dict[str, List[dict]]) -> None:
    agent_memory.write(_LOG_KEY, log)


def _normalize(data: Any) -> str:
    if isinstance(data, str):
        return data
    try:
        return json.dumps(data, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(data)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def record_interaction(agent_name: str, input_data: Any, output: Any, result: str) -> None:
    """Store interaction details in shared memory."""
    input_str = _normalize(input_data)
    output_str = _normalize(output)
    entry = {
        "hash": _hash(input_str),
        "input": input_str,
        "output": output_str,
        "result": result,
    }
    log = _load_log()
    log.setdefault(agent_name, []).append(entry)
    _save_log(log)
    log_action("Learning", f"record {agent_name} {result}")


def get_agent_hint(agent_name: str, input_data: Any) -> str | None:
    """Return best matching successful output from past interactions."""
    input_str = _normalize(input_data)
    log = _load_log()
    entries = log.get(agent_name, [])
    best_ratio = 0.0
    best_output = None
    for item in entries:
        if item.get("result") != "success":
            continue
        ratio = difflib.SequenceMatcher(None, item.get("input", ""), input_str).ratio()
        if ratio > 0.7 and ratio > best_ratio:
            best_ratio = ratio
            best_output = item.get("output")
    if best_output:
        log_action("Learning", f"hint {agent_name}")
    return best_output
