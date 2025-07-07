from __future__ import annotations

"""Suggest pipeline optimizations based on trace and learning data."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

WINDOW = 10
FAST_SECONDS = 5.0


def _load_trace(path: Path) -> Dict[str, List[dict]]:
    data: Dict[str, List[dict]] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except Exception:
            continue
        agent = entry.get("agent")
        if not agent:
            continue
        data.setdefault(agent, []).append(entry)
    return data


def _load_learning(path: Path) -> Dict[str, List[dict]]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _avg_duration(entries: List[dict]) -> float:
    durations: List[float] = []
    for item in entries:
        start = item.get("start_time")
        end = item.get("end_time")
        try:
            s = datetime.fromisoformat(start)
            e = datetime.fromisoformat(end)
            durations.append((e - s).total_seconds())
        except Exception:
            continue
    if not durations:
        return 0.0
    return sum(durations) / len(durations)


def _repeated(entries: List[dict]) -> bool:
    count: Dict[str, int] = {}
    for item in entries:
        h = item.get("hash")
        if not h:
            continue
        count[h] = count.get(h, 0) + 1
        if count[h] >= 3:
            return True
    return False


def suggest_optimizations(trace_path: str | Path, learning_path: str | Path) -> Dict[str, Any]:
    """Analyze logs and return skip/warn suggestions."""
    trace_data = _load_trace(Path(trace_path))
    learning_data = _load_learning(Path(learning_path))

    skip_flags: List[str] = []
    warn_flags: List[str] = []
    saved_time = 0.0

    for agent, t_entries in trace_data.items():
        recent_trace = t_entries[-WINDOW:]
        statuses = [e.get("status") for e in recent_trace if e.get("status")]
        all_success = statuses and all(s == "success" for s in statuses)
        avg = _avg_duration(recent_trace)
        l_entries = learning_data.get(agent, [])[-WINDOW:]
        repeat = _repeated(l_entries)

        flag = f"--skip={agent.replace('Agent', '').lower()}"
        if all_success and avg <= FAST_SECONDS and repeat:
            skip_flags.append(flag)
            saved_time += avg
        elif all_success and avg <= FAST_SECONDS:
            warn_flags.append(flag)

    opt_notes = ""
    if skip_flags:
        agents = ", ".join(a.split("=")[1].capitalize() for a in skip_flags)
        opt_notes = f"⚡ Сэкономим до {int(saved_time)} сек, если пропустить: {agents}"

    return {"skip_flags": skip_flags, "warn_flags": warn_flags, "opt_notes": opt_notes}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Suggest pipeline optimizations")
    parser.add_argument("--trace", default="agent_trace.log")
    parser.add_argument("--learning", default="agent_learning.json")
    args = parser.parse_args()
    result = suggest_optimizations(args.trace, args.learning)
    print(json.dumps(result, indent=2, ensure_ascii=False))
