# utils/apply_patch.py
"""
Применяет JSON-патч от CoderAgent и, при необходимости,
фиксирует изменения в репозитории AI-студии.

Формат патча:
{
  "modifications": [
    {
      "path": "Assets/Scripts/Feature.cs",
      "action": "overwrite",
      "content": "..."
    }
  ]
}
"""

from pathlib import Path
import git
import config

# корень репозитория инструментов (AI-Unity-Studio)
ROOT = Path(__file__).resolve().parents[1]
# абсолютный путь к Unity-проекту (может быть ВНЕ репо)
UNITY_PROJECT = Path(config.PROJECT_PATH)

def _inside_repo(file_path: Path) -> bool:
    """True, если файл физически лежит внутри репо AI-студии."""
    try:
        file_path.relative_to(ROOT)
        return True
    except ValueError:
        return False

def apply_patch(patch: dict):
    repo = git.Repo(ROOT)

    for mod in patch.get("modifications", []):
        rel_path  = mod["path"].replace("\\", "/")
        file_path = UNITY_PROJECT / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if mod["action"] == "overwrite":
            file_path.write_text(mod["content"], encoding="utf-8")
            if _inside_repo(file_path):
                repo.git.add(file_path.as_posix())
        else:
            raise NotImplementedError(f"Action '{mod['action']}' не реализован")

    # коммитим ТОЛЬКО если есть изменения внутри репо инструментов
    if repo.is_dirty():
        repo.index.commit("feat: apply AI patch")
        print(f"✅ Патч применён и закоммичен "
              f"({len(patch.get('modifications', []))} файлов)")
    else:
        print(f"✅ Патч применён во внешний проект "
              f"({len(patch.get('modifications', []))} файлов, без git-коммита)")
