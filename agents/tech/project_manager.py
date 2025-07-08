# agents/tech/project_manager.py
"""Plan tasks for a feature using local LLM."""

import json

import agent_memory
from utils.agent_journal import log_trace
from utils.llm import ask_mistral


def run(feature: dict) -> dict:
    """
    Args:
        feature: {"feature": <текст фичи>}
    Returns:
        {"tasks": [ { "feature": <текст>, "acceptance": ["Compiles"] } ]}
    """
    if not feature:
        feature = agent_memory.read("feature_description") or {}
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
            for task in tasks:
                text = " ".join([str(task.get("feature", "")), *task.get("acceptance", [])]).lower()
                attach = any(k in text for k in ["findobjectoftype", "scene", "gameobject", "добавить в сцену"])
                if any(k in text for k in ["inherits from", "base class", "используется как база", "расширяется"]):
                    ctype = "abstract"
                elif any(k in text for k in ["config asset", "data", "конфиг", "данные"]):
                    ctype = "ScriptableObject"
                elif any(k in text for k in ["utility", "utilities", "helper", "утилиты"]):
                    ctype = "static"
                else:
                    ctype = "MonoBehaviour"
                if ctype == "MonoBehaviour" and attach:
                    attach_to_scene = True
                else:
                    attach_to_scene = False
                task["component_type"] = ctype
                task["attach_to_scene"] = attach_to_scene
            result = {"tasks": tasks}
            log_trace("ProjectManagerAgent", "run", feature, result)
            agent_memory.write("tasks", result)
            return result
    except json.JSONDecodeError:
        pass
    result = {
        "tasks": [
            {"feature": desc, "acceptance": ["Compiles"], "component_type": "MonoBehaviour", "attach_to_scene": False}
        ]
    }
    log_trace("ProjectManagerAgent", "run", feature, result)
    agent_memory.write("tasks", result)
    return result
