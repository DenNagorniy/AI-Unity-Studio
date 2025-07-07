from pathlib import Path

from config import UNITY_SCRIPTS_PATH
from utils import git_tools


def save_to_unity_structure(modification):
    filename = modification["path"]
    content = modification["content"]

    target_path = Path(UNITY_SCRIPTS_PATH) / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)

    target_path.write_text(content, encoding="utf-8")
    print(f"✅ Файл сохранён в Unity проект: {target_path}")


def apply_patch(patch):
    for mod in patch.get("modifications", []):
        save_to_unity_structure(mod)

    # git add + commit (если нужно)
    git_tools.commit_changes("AI applied patch")
