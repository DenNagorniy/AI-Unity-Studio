from typing import List, Dict

def task_manager(user_prompt: str, context: str = "") -> Dict:
    """
    Простой пример разбивки запроса на задачу для кодера.

    Возвращает структуру с фичей, файлами и критериями приёмки.
    """
    # В MVP просто оборачиваем запрос в стандартную структуру
    task_spec = {
        "feature": user_prompt.strip(),
        "files": [
            {
                "path": "Assets/Scripts/Feature.cs",
                "purpose": "Основной скрипт для фичи"
            }
        ],
        "acceptance": [
            "Код компилируется без ошибок",
            "Фича соответствует описанию"
        ]
    }
    return task_spec
