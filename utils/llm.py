import json

import requests


def ask_mistral(prompt: str, model: str = "mistral") -> str:
    """Query local Mistral LLM via Ollama REST API."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"model": model, "prompt": prompt, "stream": False}),
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.RequestException as exc:
        return f"⚠ LLM error: {exc}".strip()
