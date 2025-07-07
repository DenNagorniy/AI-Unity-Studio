import json
import os
import shutil
from pathlib import Path

import ci_build
import ci_test
from run_pipeline import main as pipeline_main
from utils.agent_journal import read_entries


def main() -> None:
    if os.getenv("SKIP_PIPELINE") != "1":
        pipeline_main()

    reports = Path("ci_reports")
    reports.mkdir(exist_ok=True)
    for name in ["review_report.md", "review_report.json"]:
        if Path(name).exists():
            shutil.copy(Path(name), reports / Path(name).name)

    ci_test.main()
    ci_build.main()

    lines = read_entries()
    summary_lines = ["# Final Summary", "", "## Agent log"] + [f"- {entry}" for entry in lines[-20:]]
    try:
        test_data = json.loads(Path("ci_reports/ci_test.json").read_text(encoding="utf-8"))
        build_data = json.loads(Path("ci_reports/ci_build.json").read_text(encoding="utf-8"))
        summary_lines += [
            "",
            "## CI Results",
            f"- Tests: {'error' if 'error' in test_data else 'ok'}",
            f"- Build: {build_data.get('status', 'unknown')}",
        ]
    except Exception:
        pass

    summary = "\n".join(summary_lines)
    Path("final_summary.md").write_text(summary + "\n", encoding="utf-8")
    shutil.copy("final_summary.md", reports / "final_summary.md")
    print(summary)


if __name__ == "__main__":
    main()
