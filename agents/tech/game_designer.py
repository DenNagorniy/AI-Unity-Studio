# agents/tech/game_designer.py
"""Generate short feature description using local LLM."""

from utils.llm import ask_mistral


def run(input: dict) -> dict:
    """
    Args:
        input: {"text": <строка пользователя>}
    Returns:
        dict: {"feature": <короткое описание>}
    """
    text = input.get("text", "").strip()
    if not text:
        return {"feature": "stub feature"}
    prompt = "Summarise the following game feature idea in one short sentence:\n" + text
    feature = ask_mistral(prompt)
    return {"feature": feature or text}
