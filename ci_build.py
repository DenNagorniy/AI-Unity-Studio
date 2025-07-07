"""Build the project with Unity and store artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path

import config
from agents.tech import build_agent
from utils.feature_index import load_index, update_feature
from tools.gen_changelog import main as gen_changelog


def main() -> None:
    """Run Unity build and update project index."""

    if not Path(config.UNITY_CLI).exists():
        print(f"ERROR: Unity CLI not found at {config.UNITY_CLI}")
        return

    target = os.getenv("BUILD_TARGET", "WebGL")
    try:
        res = build_agent.run({"target": target})
        status = "built" if res.get("status") == "success" else "failed"
    except Exception as e:  # noqa: PERF203
        res = {"error": str(e)}
        status = "failed"

    index = load_index()
    for feat in index.get("features", []):
        update_feature(feat.get("id", "unknown"), feat.get("name", ""), status)

    reports_dir = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports_dir.mkdir(exist_ok=True)
    artifact = res.get("artifact")
    if artifact and Path(artifact).exists():
        path = Path(artifact)
        path.rename(reports_dir / path.name)
        res["artifact"] = str(reports_dir / path.name)

    for extra in ["build.log"]:
        p = Path(extra)
        if p.exists():
            p.rename(reports_dir / p.name)

    (reports_dir / "ci_build.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    gen_changelog()

    changelog_path = Path("CHANGELOG.md").resolve()
    artifact_path = res.get("artifact")
    artifacts = [artifact_path] if artifact_path else []

    print(json.dumps(res, indent=2, ensure_ascii=False))
    print(f"Build {status}")
    if artifacts:
        print("Artifacts:")
        for art in artifacts:
            print(f"- {art}")
    print(f"Changelog: {changelog_path}")


if __name__ == "__main__":
    main()
