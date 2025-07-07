from __future__ import annotations

from pathlib import Path

from utils.llm import ask_mistral


def coder(task_spec):
    """Generate a C# script using local LLM."""
    path = task_spec.get("path", "Generated/Feature.cs")
    namespace = task_spec.get("namespace", "AIUnityStudio.Generated")
    feature = task_spec.get("feature", "")

    class_name = Path(path).stem
    prompt = (
        f"Write a Unity C# script called {class_name} in namespace {namespace}. "
        f"The script should implement: {feature}. Provide only the code."
    )
    code = ask_mistral(prompt)

    if "namespace" not in code:
        code = f"namespace {namespace} {{\n{code}\n}}"

    return {
        "modifications": [
            {
                "path": path,
                "content": code,
                "action": "overwrite",
            }
        ]
    }


def run(task_spec):
    """Public wrapper used by the orchestrator."""
    return coder(task_spec)
