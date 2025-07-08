from __future__ import annotations

"""Generate simple scene files corresponding to generated scripts."""

import json
from pathlib import Path

import agent_memory
from utils.agent_journal import log_trace


def run(data: dict) -> dict:
    """Generate a simple scene description tied to the generated script."""

    if not data:
        data = agent_memory.read("architecture") or {}
    script_path = data.get("path", "Generated/Helper.cs")
    scene_dir = Path("Assets/Scenes/Generated")
    scene_dir.mkdir(parents=True, exist_ok=True)

    scene_name = Path(script_path).stem
    json_path = scene_dir / f"{scene_name}.json"
    scene_data = {
        "scene": scene_name,
        "monobehaviours": [script_path],
    }
    json_path.write_text(json.dumps(scene_data, indent=2), encoding="utf-8")
    result = {
        "scene": str(json_path),
        "objects": scene_data["monobehaviours"],
    }
    log_trace("SceneBuilderAgent", "run", data, result)
    agent_memory.write("scene", result)
    return result
