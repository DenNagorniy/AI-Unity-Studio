"""Generate mood board descriptions for game ideas."""

from pathlib import Path

from utils.agent_journal import log_trace
from utils.llm import ask_mistral


def run(data: dict) -> dict:
    """Generate a textual mood board description."""
    idea = data.get("text", "")
    prompt = "Create a one-paragraph mood board description for this game idea:\n" + idea
    description = ask_mistral(prompt)
    mood_dir = Path("moodboards")
    mood_dir.mkdir(exist_ok=True)
    path = mood_dir / "mood.txt"
    path.write_text(description, encoding="utf-8")
    result = {"moodboard": str(path)}
    log_trace("ArtMoodAgent", "run", data, result)
    return result
