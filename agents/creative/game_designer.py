from pathlib import Path

from utils.llm import ask_mistral
from utils.agent_journal import log_trace


def run(input: dict) -> dict:
    """Generate a short core loop description using local LLM."""
    idea = input.get("text", "").strip()
    if not idea:
        return {"core_loop": ""}
    prompt = (
        "Design a concise core gameplay loop for the following idea. "
        "Respond with a paragraph under 100 words.\n" + idea
    )
    core_loop = ask_mistral(prompt)
    Path("core_loop.md").write_text(core_loop, encoding="utf-8")
    result = {"core_loop": core_loop, "file": "core_loop.md"}
    log_trace("CreativeGameDesigner", "run", input, result)
    return result

