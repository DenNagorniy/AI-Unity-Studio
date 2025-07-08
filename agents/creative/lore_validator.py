from __future__ import annotations

"""Validate generated content against the existing lore."""

import json
import re
from pathlib import Path
from typing import Any, Dict

from utils.agent_journal import log_trace


def _load_lore() -> str:
    text = ""
    lore_dir = Path("lore")
    if lore_dir.exists():
        for path in lore_dir.iterdir():
            if path.is_file():
                text += path.read_text(encoding="utf-8") + "\n"
    lorebook = Path("lorebook.json")
    if lorebook.exists():
        try:
            data = json.loads(lorebook.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                text += " \n".join(str(v) for v in data.values())
            else:
                text += json.dumps(data, ensure_ascii=False)
        except Exception:
            text += lorebook.read_text(encoding="utf-8")
    return text.lower()


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[A-Za-zА-Яа-яёЁ]+", text.lower()) if len(t) > 2}


def run(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate feature description and dialogues against existing lore."""
    feature = data.get("feature", "unknown")
    desc = data.get("description", "")
    dialogues = data.get("dialogues", "")
    assets = data.get("assets", [])
    out_dir = Path(data.get("out_dir", "."))

    lore_text = _load_lore()
    lore_tokens = _tokens(lore_text)
    input_tokens = _tokens(desc + " " + dialogues + " " + " ".join(map(str, assets)))
    missing = sorted(input_tokens - lore_tokens)

    status = "LorePass" if not missing else "Mismatch"

    lines = [
        "# Lore Validation",
        f"**Feature:** {feature}",
        f"**Status:** {status} {'✅' if status == 'LorePass' else '⚠️'}",
        "",
    ]
    if missing:
        lines.append("## Unknown terms")
        lines.extend(f"- {m}" for m in missing)
    else:
        lines.append("All terms are present in the lore base.")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / "lore_validation.md"
    report.write_text("\n".join(lines), encoding="utf-8")

    result = {"status": status, "report": str(report)}
    log_trace("LoreValidatorAgent", "run", data, result)
    return result
