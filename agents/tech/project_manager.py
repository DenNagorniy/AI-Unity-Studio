# agents/tech/project_manager.py
"""Stub project manager that converts feature to a single task list."""


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
