"""Run full pipeline: tests, build, publish and changelog."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import ci_build
import ci_test
from ci_publish import _load_env
from ci_publish import main as publish_main
from notify import notify_all
from run_pipeline import main as pipeline_main
from tools.gen_changelog import main as gen_changelog
from tools.gen_summary import generate_summary
from utils.agent_journal import read_entries
from utils.pipeline_config import load_config
import ci_assets


def main() -> None:
    """Execute full CI pipeline."""
    cfg = load_config()

    if os.getenv("SKIP_PIPELINE") != "1":
        pipeline_main(cfg.get("agents"))

    reports = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports.mkdir(exist_ok=True)
    for name in ["review_report.md", "review_report.json"]:
        if Path(name).exists():
            shutil.copy(Path(name), reports / Path(name).name)

    ci_test.main()
    if cfg["steps"].get("build", True):
        ci_build.main()

    publish_status = "success"
    if cfg["steps"].get("publish", True):
        try:
            publish_main()
        except Exception as e:  # noqa: PERF203
            publish_status = "error"
            print(f"Publish failed: {e}")

    if cfg["steps"].get("qc", True):
        try:
            ci_assets.main()
        except Exception as e:  # noqa: PERF203
            print(f"Asset pipeline failed: {e}")

    gen_changelog()

    lines = read_entries()
    summary_lines = [
        "# Final Summary",
        "",
        "## Agent log",
        *[f"- {entry}" for entry in lines[-20:]],
    ]
    agent_results = {}
    try:
        test_data = json.loads((reports / "ci_test.json").read_text(encoding="utf-8"))
        build_data = json.loads((reports / "ci_build.json").read_text(encoding="utf-8"))
        test_status = "error" if "error" in test_data else "success"
        build_status = "success" if build_data.get("status") == "success" else "error"
        agent_results["TesterAgent"] = test_status
        agent_results["BuildAgent"] = build_status
        summary_lines += [
            "",
            "## CI Results",
            f"- Tests: {test_status}",
            f"- Build: {build_status}",
        ]
    except Exception:
        pass

    urls = []
    try:
        cfg = _load_env()
        artifacts = [p for p in reports.iterdir() if p.suffix in {".zip", ".apk"}]
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

    agent_results["Publish"] = publish_status
    summary_path = generate_summary(urls, agent_results, out_dir=str(reports))
    print(f"Summary HTML: {summary_path}")

    notify_all(str(summary_path), "CHANGELOG.md", urls)


if __name__ == "__main__":
    main()
