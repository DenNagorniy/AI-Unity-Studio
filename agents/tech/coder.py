from __future__ import annotations

"""Utilities for generating C# code using a local LLM."""

from pathlib import Path

import agent_memory
from utils.agent_journal import log_trace
from utils.llm import ask_mistral
from utils.test_generation import generate_test_files


def coder(task_spec):
    """Generate a C# script using local LLM."""
    if not task_spec:
        task_spec = agent_memory.read("architecture") or {}
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

    mods = [
        {
            "path": path,
            "content": code,
            "action": "overwrite",
        }
    ]
    mods.extend(generate_test_files(path, namespace, code))

    result = {"modifications": mods}
    log_trace("CoderAgent", "run", task_spec, result)
    agent_memory.write("patch", result)
    return result


def run(task_spec):
    """Public wrapper used by the orchestrator."""
    return coder(task_spec)
