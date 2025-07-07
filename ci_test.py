"""Run Unity tests and generate reports."""

from __future__ import annotations

import json
import os
from pathlib import Path

import config
from agents.tech import tester
from notify import notify_all
from tools.gen_changelog import main as gen_changelog
from utils.feature_index import load_index, update_feature


def main() -> None:
    """Execute Unity tests and update project index."""

    if not Path(config.UNITY_CLI).exists():
        print(f"ERROR: Unity CLI not found at {config.UNITY_CLI}")
        return

    try:
        res = tester.run({})
        status = "done"
    except Exception as e:  # noqa: PERF203
        res = {"error": str(e)}
        status = "failed"

    index = load_index()
    for feat in index.get("features", []):
        update_feature(feat.get("id", "unknown"), feat.get("name", ""), status)

    reports_dir = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports_dir.mkdir(exist_ok=True)
    for p in res.get("report_paths", []):
        path = Path(p)
        if path.exists():
            path.rename(reports_dir / path.name)

    (reports_dir / "ci_test.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    gen_changelog()

    changelog_path = Path("CHANGELOG.md").resolve()
    paths = [reports_dir / Path(p).name for p in res.get("report_paths", [])]
    artifacts = [p.as_posix() for p in paths if p.exists()]

    print(json.dumps(res, indent=2, ensure_ascii=False))
    print(f"Tests {status}")
    if artifacts:
        print("Artifacts:")
        for art in artifacts:
            print(f"- {art}")
    print(f"Changelog: {changelog_path}")

    notify_all(str(Path("ci_reports") / "summary.html"), str(changelog_path), artifacts)


if __name__ == "__main__":
    main()
