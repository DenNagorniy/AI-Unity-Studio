"""Interactive .env configuration script."""

from pathlib import Path
import shutil

ROOT_DIR = Path(__file__).resolve().parent
ENV_EXAMPLE = ROOT_DIR / ".env.example"
ENV_PATH = ROOT_DIR / ".env"


def copy_env():
    if not ENV_EXAMPLE.exists():
        raise FileNotFoundError(".env.example not found")
    if not ENV_PATH.exists():
        shutil.copy(ENV_EXAMPLE, ENV_PATH)


def update_value(lines: list[str], key: str, prompt: str) -> list[str]:
    updated = []
    for line in lines:
        if line.startswith(f"{key}="):
            current = line.split("=", 1)[1].strip()
            value = input(f"{prompt} [{current}]: ").strip() or current
            updated.append(f"{key}={value}")
        else:
            updated.append(line)
    return updated


def main() -> None:
    copy_env()
    lines = ENV_PATH.read_text().splitlines()
    lines = update_value(lines, "PROJECT_PATH", "Enter PROJECT_PATH")
    lines = update_value(lines, "UNITY_CLI", "Enter UNITY_CLI")
    lines = update_value(lines, "OPENAI_API_KEY", "Enter OPENAI_API_KEY")
    ENV_PATH.write_text("\n".join(lines) + "\n")
    print("Updated .env")


if __name__ == "__main__":
    main()
