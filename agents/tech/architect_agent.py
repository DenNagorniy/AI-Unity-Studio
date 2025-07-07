from __future__ import annotations

import json
from pathlib import Path

import config
from utils.agent_journal import log_trace
import agent_memory


def run(input: dict) -> dict:
    """Determine script path/namespace and ensure asmdef exists."""
    if not input:
        input = agent_memory.read("tasks") or agent_memory.read("feature_description") or {}
    feature = input.get("feature") or input.get("task") or (input.get("tasks") or [{}])[0].get("feature")

    if isinstance(feature, dict):
        feature = feature.get("feature")

    name = "".join(c for c in str(feature).title() if c.isalnum()) or "Feature"

    base_dir = Path(config.UNITY_SCRIPTS_PATH) / "Generated"
    base_dir.mkdir(parents=True, exist_ok=True)

    path = f"Generated/{name}.cs"
    asmdef_file = base_dir / "AIUnityStudio.Generated.asmdef"
    if not asmdef_file.exists():
        asmdef_file.write_text(
            json.dumps({"name": "AIUnityStudio.Generated"}, indent=2),
            encoding="utf-8",
        )

    result = {
        "feature": feature,
        "path": path,
        "namespace": "AIUnityStudio.Generated",
        "asmdef": asmdef_file.stem,
    }
    log_trace("ArchitectAgent", "run", input, result)
    agent_memory.write("architecture", result)
    return result
