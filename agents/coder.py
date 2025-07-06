# agents/coder.py   — v0.5 (deepseek + 90 s timeout)
from __future__ import annotations
import base64, json, re, textwrap, time
from typing import Dict
from openai import OpenAI

# ── модель (меняйте при желании только эту строку) ──────────
MODEL_NAME = "deepseek-coder:6.7b"    # phi3:mini  /  codeqwen2:7b-instruct …

client = OpenAI(api_key="ollama",
                base_url="http://localhost:11434/v1")

PROMPT_TEMPLATE = textwrap.dedent("""
    You are Unity-AI-Coder. Return ONE JSON block:

    ```
    {{
      "modifications": [
        {{
          "path": "<relative/path/File.cs>",
          "action": "overwrite",
          "encoding": "base64",
          "content": "<BASE64 STRING>"
        }}
      ]
    }}
    ```

    Encode full C# file to Base64 (UTF-8).
    NO extra text outside the triple-backtick block.

    # Feature
    {feature}

    # Acceptance
    {acceptance}
""")

# ── helpers ─────────────────────────────────────────────────
def _extract_json(txt: str) -> Dict:
    m = re.search(r"```(?:json)?\s*(\{.*?})\s*```", txt, re.S) \
        or re.search(r"(\{.*})", txt, re.S)
    if not m:
        raise ValueError("JSON-block missing")

    raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        def fix(m_):
            body = m_.group(1).replace("\\", "\\\\").replace('"', r'\"')
            return f'"content":"{body}"'
        fixed = re.sub(r'"content"\s*:\s*"(.*?)"', fix, raw, flags=re.S)
        return json.loads(fixed)

def _validate(patch: Dict):
    if not patch.get("modifications"):
        raise ValueError("no modifications")
    for m in patch["modifications"]:
        if not m["path"].endswith(".cs"):
            raise ValueError("only .cs files allowed")
        if m["action"] != "overwrite":
            raise ValueError("action must be overwrite")

# ── основной вызов ──────────────────────────────────────────
def coder(task_spec: Dict) -> Dict:
    sys_msg = {"role": "system",
               "content": "You are a concise, precise code-generation assistant."}
    base_msgs = [sys_msg]

    for attempt in range(3):                     # ≤ 3 попытки
        print(f"⏳  Coder attempt {attempt+1}/3 …", flush=True)

        prompt = PROMPT_TEMPLATE.format(
            feature=task_spec["feature"],
            acceptance="\n".join(f"- {a}" for a in task_spec["acceptance"])
        )
        msgs = base_msgs + [{"role": "user", "content": prompt}]

        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0,
                messages=msgs,
                timeout=90          # ← ждём не дольше 90 с
            )
            patch = _extract_json(resp.choices[0].message.content)
            _validate(patch)

            for mod in patch["modifications"]:
                if mod.get("encoding") == "base64":
                    decoded = (
                        base64.b64decode(mod["content"])
                        .decode("utf-8")
                        .replace("\\n", "\n")
                        .replace("\\t", "\t")
                    )
                    if not decoded.endswith("\n"):
                        decoded += "\n"
                    mod["content"] = decoded
                    mod.pop("encoding", None)
            return patch

        except Exception as err:
            print(f"⚠️  Attempt {attempt+1} failed: {err}", flush=True)
            if attempt == 2:
                raise
            time.sleep(1)
            base_msgs.append(
                {"role": "system",
                 "content": f"Previous answer invalid ({err}). "
                            f"Return VALID JSON only."})

# ── mini-test ───────────────────────────────────────────────
if __name__ == "__main__":
    print(json.dumps(coder({
        "feature": "Create empty MonoBehaviour",
        "acceptance": ["Compiles"]
    }), indent=2, ensure_ascii=False))
