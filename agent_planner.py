"""Pipeline planner for agent execution order."""

from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import List


_MEMORY_PATH = Path("agent_memory.json")
_PROJECT_MAP_PATH = Path("project_map.json")
_AGENTS_PATH = Path("AGENTS.md")

_SIM_THRESHOLD = 0.75


def _parse_baseline_agents() -> List[str]:
    """Return engineering agents order from AGENTS.md."""
    if not _AGENTS_PATH.exists():
        return []
    lines = _AGENTS_PATH.read_text(encoding="utf-8").splitlines()
    agents: List[str] = []
    in_table = False
    for line in lines:
        if line.startswith("## ") and "Engineering" in line:
            in_table = True
            continue
        if in_table and line.startswith("###"):
            break
        if in_table and line.strip().startswith("|"):
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) >= 1 and parts[0] and not parts[0].startswith("-"):
                name = parts[0].split()[0]
                if name and "Agent" in name:
                    agents.append(name)
    return agents


_BASELINE_PLAN = _parse_baseline_agents()


def _collect_known_features() -> List[str]:
    """Gather feature names from memory and project map."""
    feats: List[str] = []
    if _MEMORY_PATH.exists():
        try:
            mem = json.loads(_MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            mem = {}

        def _walk(value):
            if isinstance(value, dict):
                if isinstance(value.get("feature"), str):
                    feats.append(value["feature"])
                for v in value.values():
                    _walk(v)
            elif isinstance(value, list):
                for item in value:
                    _walk(item)
        _walk(mem)
    if _PROJECT_MAP_PATH.exists():
        try:
            data = json.loads(_PROJECT_MAP_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for feat in data.get("features", {}).values():
            name = feat.get("name")
            if isinstance(name, str):
                feats.append(name)
    return feats


def _has_similar_feature(prompt: str, known: List[str]) -> bool:
    """Check if prompt is similar to any known feature."""
    prompt_low = prompt.lower()
    for feat in known:
        ratio = SequenceMatcher(None, prompt_low, feat.lower()).ratio()
        if ratio >= _SIM_THRESHOLD:
            return True
    return False


def _apply_rules(plan: List[str], prompt: str) -> List[str]:
    """Apply simple rule engine to adjust plan."""
    p = prompt.lower()
    if ("visual" in p or "scene" in p or "prefab" in p) and "SceneBuilderAgent" not in plan:
        idx = plan.index("ArchitectAgent") + 1 if "ArchitectAgent" in plan else len(plan)
        plan.insert(idx, "SceneBuilderAgent")
    if "visual" not in p and "scene" not in p:
        plan = [a for a in plan if a != "SceneBuilderAgent"]
    return plan


def plan_pipeline(prompt: str) -> List[str]:
    """Return ordered list of agents for the given feature prompt."""
    if not prompt:
        return _BASELINE_PLAN

    known = _collect_known_features()
    plan = list(_BASELINE_PLAN)
    if _has_similar_feature(prompt, known):
        plan = [a for a in plan if a not in {"GameDesignerAgent", "ProjectManagerAgent"}]
    plan = _apply_rules(plan, prompt)
    return plan


if __name__ == "__main__":
    import sys

    text = sys.argv[1] if len(sys.argv) > 1 else "sample feature"
    print(plan_pipeline(text))
