"""Interactive .env configuration script."""

from pathlib import Path
import os
import shutil

ROOT_DIR = Path(__file__).resolve().parent
ENV_EXAMPLE = ROOT_DIR / ".env.example"
ENV_PATH = ROOT_DIR / ".env"


def copy_env():
    if not ENV_EXAMPLE.exists():
        raise FileNotFoundError(".env.example not found")
    if not ENV_PATH.exists():
        shutil.copy(ENV_EXAMPLE, ENV_PATH)


def ask_value(key: str, prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def quote_if_needed(value: str) -> str:
    value = value.strip()
    if " " in value and not (value.startswith('"') and value.endswith('"')):
        return f'"{value}"'
    return value


def main() -> None:
    copy_env()
    env = {}
    for line in ENV_PATH.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k] = v

    project = ask_value("PROJECT_PATH", "Enter PROJECT_PATH", env.get("PROJECT_PATH", ""))
    project = quote_if_needed(project)

    unity_cli = ask_value("UNITY_CLI", "Enter UNITY_CLI", env.get("UNITY_CLI", ""))
    unity_cli = quote_if_needed(unity_cli)

    scripts_default = env.get("UNITY_SCRIPTS_PATH", "")
    scripts = ask_value("UNITY_SCRIPTS_PATH", "Enter UNITY_SCRIPTS_PATH", scripts_default)
    if not scripts:
        scripts = os.path.join(os.path.dirname(project.strip('"')), "Scripts")
    scripts = quote_if_needed(scripts)

    openai = ask_value("OPENAI_API_KEY", "Enter OPENAI_API_KEY", env.get("OPENAI_API_KEY", ""))
    openai = openai.strip('"')

    lines = [
        f"PROJECT_PATH={project}",
        f"UNITY_CLI={unity_cli}",
        f"UNITY_SCRIPTS_PATH={scripts}",
        f"OPENAI_API_KEY={openai}",
    ]

    ENV_PATH.write_text("\n".join(lines) + "\n")
    print("Updated .env")


if __name__ == "__main__":
    main()
