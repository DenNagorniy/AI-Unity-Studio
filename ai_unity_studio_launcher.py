"""Launch AI Unity Studio dashboard."""

from pathlib import Path
import subprocess
import sys
import webbrowser

SCRIPT_DIR = Path(__file__).resolve().parent
DASHBOARD = SCRIPT_DIR / "dashboard.py"


def main() -> None:
    proc = subprocess.Popen([
        sys.executable,
        str(DASHBOARD),
        "--serve",
    ], cwd=SCRIPT_DIR)

    overview_path = Path("ci_reports") / "ci_overview.html"
    if overview_path.exists():
        url = "http://localhost:8000/overview"
    else:
        url = "http://localhost:8000/ci-status"
        print(
            "[info] Overview not found. Opened /ci-status instead. "
            "Run run_all.py to generate full overview."
        )

    webbrowser.open(url)
    proc.wait()


if __name__ == "__main__":
    main()
