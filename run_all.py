import shutil
from pathlib import Path

import ci_build
import ci_test
from run_pipeline import main as pipeline_main


def main() -> None:
    pipeline_main()

    reports = Path("ci_reports")
    reports.mkdir(exist_ok=True)
    for name in ["review_report.md", "review_report.json"]:
        if Path(name).exists():
            shutil.copy(Path(name), reports / Path(name).name)

    ci_test.main()
    ci_build.main()


if __name__ == "__main__":
    main()
