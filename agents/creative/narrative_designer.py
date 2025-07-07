import json
from pathlib import Path
from utils.llm import ask_mistral


def run(input: dict) -> dict:
    """Create a simple narrative event JSON based on core loop."""
    core_loop = input.get("core_loop", "")
    prompt = (
        "Create a short intro scene for the following game core loop as JSON with "
        "fields 'scene' and 'dialogue' (list of lines).\n" + core_loop
    )
    reply = ask_mistral(prompt)
    scene_dir = Path("narrative_events")
    scene_dir.mkdir(parents=True, exist_ok=True)
    scene_path = scene_dir / "scene_1.json"
    try:
        json.loads(reply)
        scene_path.write_text(reply, encoding="utf-8")
    except json.JSONDecodeError:
        scene = {"scene": "intro", "dialogue": [reply]}
        scene_path.write_text(json.dumps(scene, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"scene": str(scene_path)}
