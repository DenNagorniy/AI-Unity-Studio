from __future__ import annotations

import json
from pathlib import Path

from agents.tech import coder, refactor_agent, scene_builder_agent
from utils.agent_journal import log_auto_fix
from utils.apply_patch import apply_patch

AGENT_MAP = {
    "CoderAgent": coder,
    "TesterAgent": coder,
    "RefactorAgent": refactor_agent,
    "SceneBuilderAgent": scene_builder_agent,
    "BuildAgent": refactor_agent,
}


def auto_fix(feature_name: str, agent_name: str, error: str) -> bool:
    """Attempt automatic fix for a failing pipeline step."""
    log_auto_fix(agent_name, "start", error)
    patch_dir = Path("patches")
    patch_dir.mkdir(exist_ok=True)
    module = AGENT_MAP.get(agent_name, coder)
    try:
        result = module.run({"feature": feature_name, "error": error})
    except Exception as exc:  # noqa: PERF203
        log_auto_fix(agent_name, "error", str(exc))
        return False

    if not isinstance(result, dict) or "modifications" not in result:
        log_auto_fix(agent_name, "noop", "no patch returned")
        return False

    patch_file = patch_dir / f"{feature_name}_{agent_name}.json"
    patch_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        apply_patch(result)
        log_auto_fix(agent_name, "success", f"applied {patch_file.name}")
        return True
    except Exception as exc:  # noqa: PERF203
        log_auto_fix(agent_name, "error", str(exc))
        return False
