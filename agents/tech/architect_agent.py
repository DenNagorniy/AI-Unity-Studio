from __future__ import annotations
from pathlib import Path
import json
import config


def run(input: dict) -> dict:
    """Determine script path/namespace and ensure asmdef exists."""
    feature = input.get("feature") or input.get("task") or (input.get("tasks") or [{}])[0].get("feature")

    if isinstance(feature, dict):
        feature = feature.get("feature")

    name = "".join(c for c in str(feature).title() if c.isalnum()) or "Feature"

    base_dir = Path(config.UNITY_SCRIPTS_PATH) / "Generated"
    base_dir.mkdir(parents=True, exist_ok=True)

    # Relative path from UNITY_SCRIPTS_PATH
    path = f"Generated/{name}.cs"
    asmdef_file = base_dir / "AIUnityStudio.Generated.asmdef"
    if not asmdef_file.exists():
        asmdef_file.write_text(
            json.dumps({"name": "AIUnityStudio.Generated"}, indent=2),
            encoding="utf-8",
        )

    return {
        "feature": feature,
        "path": path,
        "namespace": "AIUnityStudio.Generated",
        "asmdef": asmdef_file.stem,
    }
