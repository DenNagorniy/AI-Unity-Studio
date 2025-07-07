from __future__ import annotations

import base64
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from PIL import Image

INVOKE_URL = os.getenv("INVOKEAI_URL", "http://127.0.0.1:9090")
BLENDER_CLI = os.getenv("BLENDER_CLI", "blender")
ASSET_ROOT = Path("Assets")
CATALOG_PATH = Path("asset_catalog.json")


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "asset"


def _load_catalog() -> dict[str, Any]:
    if CATALOG_PATH.exists():
        with CATALOG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"assets": []}


def _save_catalog(data: dict[str, Any]) -> None:
    CATALOG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _add_entry(path: Path, asset_type: str) -> None:
    catalog = _load_catalog()
    catalog.setdefault("assets", []).append(
        {
            "path": str(path),
            "type": asset_type,
            "created": datetime.utcnow().isoformat(),
        }
    )
    _save_catalog(catalog)


def _generate_texture(prompt: str, out_path: Path) -> Path:
    payload = {"prompt": prompt, "steps": 30}
    resp = requests.post(f"{INVOKE_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    img_data = base64.b64decode(data["images"][0])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(img_data)
    _create_texture_preview(out_path)
    _add_entry(out_path, "texture")
    return out_path


def _create_texture_preview(path: Path) -> None:
    preview = path.with_name(path.stem + "_preview.png")
    with Image.open(path) as img:
        img.thumbnail((512, 512))
        img.save(preview)


def _render_preview(model_path: Path) -> None:
    preview_path = model_path.with_name(model_path.stem + "_preview.png")
    script = f"""
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"{model_path}")
bpy.context.scene.render.filepath = r"{preview_path}"
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.ops.render.render(write_still=True)
"""
    subprocess.run([BLENDER_CLI, "-b", "-P", "-"], input=script.encode(), check=True)


def _generate_model(prompt: str, out_path: Path) -> Path:
    shape = "cube"
    text = prompt.lower()
    if "sphere" in text:
        shape = "uv_sphere"
    elif "cylinder" in text:
        shape = "cylinder"
    elif "cone" in text:
        shape = "cone"
    elif "plane" in text:
        shape = "plane"
    script = f"""
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
if '{shape}' == 'uv_sphere':
    bpy.ops.mesh.primitive_uv_sphere_add()
elif '{shape}' == 'cylinder':
    bpy.ops.mesh.primitive_cylinder_add()
elif '{shape}' == 'cone':
    bpy.ops.mesh.primitive_cone_add()
elif '{shape}' == 'plane':
    bpy.ops.mesh.primitive_plane_add()
else:
    bpy.ops.mesh.primitive_cube_add()
bpy.ops.export_scene.gltf(filepath=r"{out_path}", export_format='GLB')
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([BLENDER_CLI, "-b", "-P", "-"], input=script.encode(), check=True)
    _render_preview(out_path)
    _add_entry(out_path, "model")
    return out_path


def generate_asset(asset_type: str, description: str, category: str = "Environment") -> Path:
    folder = ASSET_ROOT / category
    folder.mkdir(parents=True, exist_ok=True)
    name = _slugify(description)
    if asset_type == "model":
        out_path = folder / f"{name}.glb"
        return _generate_model(description, out_path)
    out_path = folder / f"{name}.png"
    return _generate_texture(description, out_path)


def generate_from_specs(specs: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    for item in specs:
        try:
            p = generate_asset(
                item.get("type", "texture"),
                item.get("description", ""),
                item.get("category", "Environment"),
            )
            paths.append(str(p))
        except Exception as e:  # noqa: PERF203
            paths.append(f"error: {e}")
    return paths
