import json

import requests


def ask_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"model": "mistral", "prompt": prompt, "stream": False}),
            timeout=5,  # на всякий случай
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response field in Ollama reply")
    except requests.exceptions.ConnectionError:
        return "⚠ Ollama server not running on localhost:11434"
    except Exception as e:
        return f"⚠ Unexpected error: {e}"


if __name__ == "__main__":
    code = ask_ollama("Create static utility class MathHelper with method public static int Square(int x)")
    print(code)
