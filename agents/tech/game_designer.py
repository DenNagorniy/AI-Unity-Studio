# agents/tech/game_designer.py
"""Generate short feature description using local LLM."""

import json

import agent_memory
from utils.agent_journal import log_trace
from utils.llm import ask_mistral


def run(input: dict) -> dict:
    """
    Args:
        input: {"text": <строка пользователя>}
    Returns:
        dict: {"feature": <короткое описание>}
    """
    text = input.get("text", "")
    if isinstance(text, str):
        text = text.strip()
    elif isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    else:
        text = str(text).strip()
    if not text:
        return {"feature": "stub feature"}
    prompt = "Summarise the following game feature idea in one short sentence:\n" + text
    feature = ask_mistral(prompt)
    result = {"feature": feature or text}
    log_trace("GameDesignerAgent", "run", input, result)
    agent_memory.write("feature_description", result)
    return result
