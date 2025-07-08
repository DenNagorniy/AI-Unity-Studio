from pathlib import Path
import subprocess
import sys

from pipeline_config import get_config


def main() -> None:
    msg = sys.argv[1] if len(sys.argv) > 1 else "AI patch"
    cfg = get_config()
    target = cfg["scripts_path"]
    subprocess.run(["git", "add", str(target)], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)


if __name__ == "__main__":
    main()
