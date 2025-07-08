from __future__ import annotations

"""Plan script locations and namespaces for generated features."""

import json
from pathlib import Path

import agent_memory
import config
from utils.agent_journal import log_trace


def run(data: dict) -> dict:
    """Determine script path/namespace and ensure asmdef exists."""
    if not data:
        data = agent_memory.read("tasks") or agent_memory.read("feature_description") or {}
    feature = data.get("feature") or data.get("task") or (data.get("tasks") or [{}])[0].get("feature")

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
    log_trace("ArchitectAgent", "run", data, result)
    agent_memory.write("architecture", result)
    return result
