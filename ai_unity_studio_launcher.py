"""Launch AI Unity Studio dashboard."""

from pathlib import Path
import subprocess
import sys
import webbrowser

SCRIPT_DIR = Path(__file__).resolve().parent
DASHBOARD = SCRIPT_DIR / "dashboard.py"


def main() -> None:
    proc = subprocess.Popen([sys.executable, str(DASHBOARD), "--serve"], cwd=SCRIPT_DIR)
    webbrowser.open("http://localhost:8000/overview")
    proc.wait()


if __name__ == "__main__":
    main()
