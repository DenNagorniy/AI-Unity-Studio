from __future__ import annotations

"""Generate simple scene files corresponding to generated scripts."""

from pathlib import Path

import agent_memory
from utils.agent_journal import log_trace


def run(data: dict) -> dict:
    """Generate a simple scene description tied to the generated script."""

    if not data:
        data = agent_memory.read("architecture") or {}

    script_path = data.get("path", "Generated/Helper.cs")
    attach = data.get("attach_to_scene", False)

    scene_dir = Path("Assets/Scenes/Generated")
    scene_dir.mkdir(parents=True, exist_ok=True)

    comp_name = Path(script_path).stem
    scene_name = f"{comp_name}_Test"
    scene_path = scene_dir / f"{scene_name}.unity"

    if attach:
        scene_content = (
            "%YAML 1.0\n"
            "%TAG !u! tag:unity3d.com,2011:\n"
            "--- !u!1 &1\n"
            "GameObject:\n"
            f"  m_Name: Feature_{comp_name}\n"
            "  m_Component:\n"
            f"  - component: {comp_name}\n"
        )
        scene_path.write_text(scene_content, encoding="utf-8")
    else:
        # create empty scene placeholder
        scene_path.write_text("%YAML 1.0\n%TAG !u! tag:unity3d.com,2011:\n", encoding="utf-8")

    result = {"scene_path": str(scene_path)}
    log_trace("SceneBuilderAgent", "run", data, result)
    agent_memory.write("scene", result)
    return result
