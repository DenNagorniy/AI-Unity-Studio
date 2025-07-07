import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_PATH = os.getenv("PROJECT_PATH", "/tmp/unity-project")
UNITY_CLI = os.getenv("UNITY_CLI", "unity")
UNITY_SCRIPTS_PATH = os.getenv("UNITY_SCRIPTS_PATH", "/tmp/unity-scripts")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # optional for local LLM

def validate_env() -> None:
    """Warn if critical environment variables are not set."""
    if PROJECT_PATH == "/tmp/unity-project":
        print("WARNING: PROJECT_PATH not set, using /tmp/unity-project")
    if UNITY_CLI == "unity":
        print("WARNING: UNITY_CLI not set, using 'unity'")
    if UNITY_SCRIPTS_PATH == "/tmp/unity-scripts":
        print("WARNING: UNITY_SCRIPTS_PATH not set, using /tmp/unity-scripts")

validate_env()
