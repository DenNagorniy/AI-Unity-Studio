# agents/tech/project_manager.py
"""Plan tasks for a feature using local LLM."""

import json

from utils.llm import ask_mistral
from utils.agent_journal import log_trace


def run(feature: dict) -> dict:
    """
    Args:
        feature: {"feature": <текст фичи>}
    Returns:
        {"tasks": [ { "feature": <текст>, "acceptance": ["Compiles"] } ]}
    """
    desc = feature.get("feature", "")
    prompt = (
        "Create 3 short development tasks to implement the following Unity feature. "
        'Respond with JSON in the form {"tasks": [{"feature": str, "acceptance": [str]}]}\n' + desc
    )
    reply = ask_mistral(prompt)
    try:
        data = json.loads(reply)
        tasks = data.get("tasks")
        if isinstance(tasks, list):
            result = {"tasks": tasks}
            log_trace("ProjectManagerAgent", "run", feature, result)
            return result
    except json.JSONDecodeError:
        pass
    result = {"tasks": [{"feature": desc, "acceptance": ["Compiles"]}]}
    log_trace("ProjectManagerAgent", "run", feature, result)
    return result

