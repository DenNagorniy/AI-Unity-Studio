from __future__ import annotations
import json
from pathlib import Path

def run(input: dict) -> dict:
    """Generate a simple scene description tied to the generated script."""

    script_path = input.get("path", "Generated/Helper.cs")
    scene_dir = Path("Assets/Scenes/Generated")
    scene_dir.mkdir(parents=True, exist_ok=True)

    scene_name = Path(script_path).stem
    json_path = scene_dir / f"{scene_name}.json"
    scene_data = {
        "scene": scene_name,
        "monobehaviours": [script_path],
    }
    json_path.write_text(json.dumps(scene_data, indent=2), encoding="utf-8")
    return {
        "scene": str(json_path),
        "objects": scene_data["monobehaviours"],
    }
