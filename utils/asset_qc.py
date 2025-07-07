from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image

MAX_TEXTURE_RESOLUTION = 2048
MAX_POLYGONS = 5000
QC_REPORT_PATH = Path("asset_qc.json")


def _check_texture(path: Path, max_size: int) -> Tuple[bool, int, int]:
    """Return True if texture is within size, along with its resolution."""
    with Image.open(path) as img:
        width, height = img.width, img.height
    return width <= max_size and height <= max_size, width, height


def _count_obj_polygons(path: Path) -> int:
    count = 0
    with path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("f "):
                count += 1
    return count


def _has_zero_pivot_obj(path: Path) -> bool:
    with path.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.strip().split()
                if len(parts) == 4 and all(abs(float(x)) < 1e-6 for x in parts[1:]):
                    return True
                break
    return False


def run_qc(
    asset_dir: str = "Assets",
    max_texture: int = MAX_TEXTURE_RESOLUTION,
    max_polygons: int = MAX_POLYGONS,
) -> List[Dict[str, str]]:
    """Scan asset directory and produce QC report as a list of issues."""
    issues: List[Dict[str, str]] = []
    for root, _dirs, files in os.walk(asset_dir):
        for name in files:
            path = Path(root) / name
            ext = path.suffix.lower()
            if ext in {".png", ".jpg", ".jpeg"}:
                ok, w, h = _check_texture(path, max_texture)
                if not ok:
                    issues.append({"asset": str(path), "issue": f"texture {w}x{h} exceeds {max_texture}"})
            elif ext == ".obj":
                polys = _count_obj_polygons(path)
                if polys > max_polygons:
                    issues.append({"asset": str(path), "issue": f"polycount {polys} exceeds {max_polygons}"})
                if not _has_zero_pivot_obj(path):
                    issues.append({"asset": str(path), "issue": "pivot not at origin"})
    QC_REPORT_PATH.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")
    return issues
