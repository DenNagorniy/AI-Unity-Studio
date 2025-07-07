from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

INDEX_PATH = Path("feature_index.json")


def load_index() -> Dict[str, Any]:
    if INDEX_PATH.exists():
        with INDEX_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {"schema_version": 1, "features": []}


def save_index(data: Dict[str, Any]) -> None:
    INDEX_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_feature(feat_id: str) -> Dict[str, Any] | None:
    data = load_index()
    for feat in data.get("features", []):
        if feat.get("id") == feat_id:
            return feat
    return None


def update_feature(feat_id: str, name: str, status: str) -> None:
    data = load_index()
    feats: List[Dict[str, Any]] = data.setdefault("features", [])
    for feat in feats:
        if feat.get("id") == feat_id:
            feat.update({"name": name, "status": status})
            break
    else:
        feats.append({"id": feat_id, "name": name, "status": status})
    save_index(data)
