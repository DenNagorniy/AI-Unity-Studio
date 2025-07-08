import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv


def get_config() -> Dict[str, Any]:
    """Load and validate configuration from .env."""
    load_dotenv()

    project_path = Path(os.getenv("PROJECT_PATH", ""))
    if not project_path.is_dir():
        raise RuntimeError(f"PROJECT_PATH not found: {project_path}")

    scripts_rel = os.getenv("UNITY_SCRIPTS_PATH")
    if not scripts_rel:
        raise RuntimeError("UNITY_SCRIPTS_PATH not set")
    if Path(scripts_rel).is_absolute():
        raise RuntimeError("UNITY_SCRIPTS_PATH must be relative")

    scripts_path = project_path / scripts_rel
    if not scripts_path.exists():
        raise RuntimeError(f"UNITY_SCRIPTS_PATH not found: {scripts_path}")

    unity_cli = os.getenv("UNITY_CLI")
    if not unity_cli:
        raise RuntimeError("UNITY_CLI not set")
    unity_cli_path = Path(unity_cli)
    if not unity_cli_path.exists():
        raise RuntimeError(f"UNITY_CLI not found: {unity_cli_path}")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    return {
        "project_path": project_path,
        "scripts_path": scripts_path,
        "unity_cli": unity_cli_path,
        "openai_api_key": openai_api_key,
    }
