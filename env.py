from pathlib import Path
import sys

from config import PROJECT_PATH, UNITY_SCRIPTS_PATH, UNITY_CLI, OPENAI_API_KEY


def validate() -> bool:
    ok = True
    if not Path(PROJECT_PATH).exists():
        print(f"❌ PROJECT_PATH not found: {PROJECT_PATH}")
        ok = False
    scripts_dir = Path(PROJECT_PATH) / UNITY_SCRIPTS_PATH
    if not scripts_dir.exists():
        print(f"❌ UNITY_SCRIPTS_PATH not found: {scripts_dir}")
        ok = False
    if not Path(UNITY_CLI).exists():
        print(f"❌ UNITY_CLI not found: {UNITY_CLI}")
        ok = False
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        ok = False
    return ok


if __name__ == "__main__":
    if validate():
        print("✅ Environment looks OK")
    else:
        sys.exit(1)
