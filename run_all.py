"""Run full pipeline: tests, build, publish and changelog."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import ci_build
import ci_test
from ci_publish import _load_env, main as publish_main
from run_pipeline import main as pipeline_main
from tools.gen_changelog import main as gen_changelog
from utils.agent_journal import read_entries


def main() -> None:
    """Execute full CI pipeline."""

    if os.getenv("SKIP_PIPELINE") != "1":
        pipeline_main()

    reports = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports.mkdir(exist_ok=True)
    for name in ["review_report.md", "review_report.json"]:
        if Path(name).exists():
            shutil.copy(Path(name), reports / Path(name).name)

    ci_test.main()
    ci_build.main()

    try:
        publish_main()
    except Exception as e:  # noqa: PERF203
        print(f"Publish failed: {e}")

    gen_changelog()

    lines = read_entries()
    summary_lines = [
        "# Final Summary",
        "",
        "## Agent log",
        *[f"- {entry}" for entry in lines[-20:]],
    ]
    try:
        test_data = json.loads(
            (reports / "ci_test.json").read_text(encoding="utf-8")
        )
        build_data = json.loads(
            (reports / "ci_build.json").read_text(encoding="utf-8")
        )
        summary_lines += [
            "",
            "## CI Results",
            f"- Tests: {'error' if 'error' in test_data else 'ok'}",
            f"- Build: {build_data.get('status', 'unknown')}",
        ]
    except Exception:
        pass

    try:
        cfg = _load_env()
        artifacts = [
            p for p in reports.iterdir() if p.suffix in {".zip", ".apk"}
        ]
        base = cfg["S3_ENDPOINT"].rstrip("/")
        urls = [f"{base}/{cfg['S3_BUCKET']}/{p.name}" for p in artifacts]
        if urls:
            summary_lines += ["", "## Artifacts", *[f"- {u}" for u in urls]]
    except Exception:
        pass

    summary_lines.append("")
    summary_lines.append(f"CHANGELOG: {Path('CHANGELOG.md').resolve()}")

    summary = "\n".join(summary_lines)
    Path("final_summary.md").write_text(summary + "\n", encoding="utf-8")
    shutil.copy("final_summary.md", reports / "final_summary.md")
    print(summary)


if __name__ == "__main__":
    main()
