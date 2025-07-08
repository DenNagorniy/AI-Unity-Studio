from pathlib import Path
import subprocess
import sys

from config import PROJECT_PATH, UNITY_SCRIPTS_PATH


def main() -> None:
    msg = sys.argv[1] if len(sys.argv) > 1 else "AI patch"
    target = Path(PROJECT_PATH) / UNITY_SCRIPTS_PATH
    subprocess.run(["git", "add", str(target)], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)


if __name__ == "__main__":
    main()
