import os

def apply_patch(patch: dict, project_path: str):
    """
    Применяет патч к файлам в проекте Unity.
    patch: {
        "modifications": [
            {
                "path": "Assets/Scripts/AI/EnemyPatrol.cs",
                "action": "overwrite",
                "content": "код"
            }, ...
        ]
    }
    project_path — абсолютный путь к unity-ai-lab
    """
    for mod in patch.get("modifications", []):
        file_path = os.path.join(project_path, mod["path"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if mod["action"] == "overwrite":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(mod["content"])
        else:
            # Можно расширять, например, append и др.
            raise NotImplementedError(f"Action {mod['action']} не реализован")

    print(f"✅ Патч применён: {len(patch.get('modifications', []))} файлов обновлено")
