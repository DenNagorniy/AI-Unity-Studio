import requests
import json

def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
    )
    result = response.json()
    return result["response"]

code = ask_ollama("Create static utility class MathHelper with method public static int Square(int x)")
print(code)
