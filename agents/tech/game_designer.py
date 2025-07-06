# agents/tech/game_designer.py
"""Stub agent to convert text prompt into feature description."""


def run(input: dict) -> dict:
    """
    Args:
        input: {"text": <строка пользователя>}
    Returns:
        dict: {"feature": <короткое описание>}
    """
    text = input.get("text", "").strip()
    return {"feature": text or "stub feature"}
