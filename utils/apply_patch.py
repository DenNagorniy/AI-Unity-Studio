from pathlib import Path

from config import PROJECT_PATH, UNITY_SCRIPTS_PATH


def normalize_path(p: str | Path) -> Path:
    parts = Path(p).parts
    if "Assets" in parts:
        idx = parts.index("Assets")
        return Path(*parts[idx:])
    return Path(p)


def save_to_unity_structure(modification):
    filename = modification["path"]
    content = modification["content"]

    rel = normalize_path(filename)
    if len(rel.parts) >= 2 and rel.parts[0] == "Assets" and rel.parts[1] in ("Scripts", "Tests"):
        rel = Path(*rel.parts[2:])
    elif rel.parts and rel.parts[0] in ("Scripts", "Tests"):
        rel = Path(*rel.parts[1:])

    target_path = Path(PROJECT_PATH) / UNITY_SCRIPTS_PATH / rel
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")
    print(f"✅ Файл сохранён в Unity проект: {target_path}")


def apply_patch(patch):
    for mod in patch.get("modifications", []):
        save_to_unity_structure(mod)

    print("📝 Patch applied, but not committed. Use commit_applied_patch.py if needed.")
