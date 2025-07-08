"""Coordinate creative agents to build a full idea specification."""

import json
from pathlib import Path

from utils.agent_journal import log_trace

from . import art_mood, game_designer, lore_keeper, narrative_designer


def run(data: dict) -> dict:
    """Run the creative pipeline and store idea_spec.json."""
    idea_text = data.get("text", "")
    gd = game_designer.run({"text": idea_text})
    scene = narrative_designer.run(gd)
    lore = lore_keeper.run(scene)
    mood = art_mood.run({"text": idea_text})
    spec = {
        "core_loop": gd.get("core_loop"),
        "scene": scene.get("scene"),
        "lorebook": lore.get("lorebook"),
        "moodboard": mood.get("moodboard"),
    }
    Path("idea_spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    log_trace("CreativeOrchestrator", "run", data, spec)
    return spec
