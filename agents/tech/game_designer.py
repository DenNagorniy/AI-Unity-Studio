# agents/tech/game_designer.py
"""
Stub-агент: получает текстовый запрос и формирует минимальное описание фичи.
"""

def run(input: dict) -> dict:
    """
    Args:
        input: {"text": <строка пользователя>}
    Returns:
        dict: {"feature": <короткое описание>}
    """
    text = input.get("text", "").strip()
    return {"feature": text or "stub feature"}
