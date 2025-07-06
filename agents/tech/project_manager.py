# agents/tech/project_manager.py
"""
Stub-ProjectManager: превращает описание фичи в список одной задачи.
"""

def run(feature: dict) -> dict:
    """
    Args:
        feature: {"feature": <текст фичи>}
    Returns:
        {"tasks": [ { "feature": <текст>, "acceptance": ["Compiles"] } ]}
    """
    return {
        "tasks": [
            {
                "feature": feature["feature"],
                "acceptance": ["Compiles"]
            }
        ]
    }
