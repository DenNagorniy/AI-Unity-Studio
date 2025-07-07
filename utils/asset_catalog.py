from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

MANIFEST_PATH = Path("asset_manifest.json")


def catalog_assets(asset_dir: str = "Assets") -> List[Dict[str, int | str]]:
    """Scan assets directory and generate manifest file."""
    entries: List[Dict[str, int | str]] = []
    for root, _dirs, files in os.walk(asset_dir):
        for name in files:
            path = Path(root) / name
            entries.append(
                {
                    "path": str(path),
                    "size": path.stat().st_size,
                    "type": path.suffix.lower().lstrip("."),
                }
            )
    MANIFEST_PATH.write_text(json.dumps({"assets": entries}, indent=2, ensure_ascii=False), encoding="utf-8")
    return entries
