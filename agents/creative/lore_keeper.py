import json
from pathlib import Path
from utils.llm import ask_mistral


def run(input: dict) -> dict:
    """Update lorebook with facts extracted from the narrative scene."""
    scene_file = input.get("scene")
    text = ""
    if scene_file and Path(scene_file).exists():
        text = Path(scene_file).read_text(encoding="utf-8")
    prompt = (
        "Extract key lore facts from the following narrative scene and return "
        "them as a JSON object of named facts.\n" + text
    )
    reply = ask_mistral(prompt)
    lore_path = Path("lorebook.json")
    if lore_path.exists():
        lore = json.loads(lore_path.read_text(encoding="utf-8"))
    else:
        lore = {}
    try:
        facts = json.loads(reply)
        if isinstance(facts, dict):
            lore.update(facts)
        else:
            lore[str(len(lore))] = facts
    except json.JSONDecodeError:
        lore[str(len(lore))] = reply
    lore_path.write_text(json.dumps(lore, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"lorebook": str(lore_path)}
