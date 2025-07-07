"""Generate HTML summary for CI pipeline."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "summary.html.j2"


def _render(
    artifact_urls: Iterable[str],
    agent_results: dict[str, str],
    metadata: dict[str, str],
    changelog: str,
    feedback: str,
    meta: str = "",
    self_improvement: str = "",
) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    return template.render(
        artifact_urls=list(artifact_urls),
        agent_results=agent_results,
        metadata=metadata,
        changelog=changelog,
        feedback=feedback,
        meta=meta,
        self_improvement=self_improvement,
    )


def generate_summary(
    artifact_urls: list[str],
    agent_results: dict[str, str],
    feedback: str = "",
    meta_insights: str = "",
    self_improvement: str = "",
    out_dir: str = "ci_reports",
) -> Path:
    """Create summary.html from given data."""
    metadata = {
        "date": datetime.utcnow().isoformat(),
        "git_commit": subprocess.check_output([
            "git",
            "rev-parse",
            "HEAD",
        ]).decode().strip(),
        "user": os.getenv("USER", "unknown"),
    }
    changelog_path = Path("CHANGELOG.md")
    changelog = (
        changelog_path.read_text(encoding="utf-8")
        if changelog_path.exists()
        else ""
    )

    asset_report = Path(out_dir) / "assets_report.html"
    if asset_report.exists():
        artifact_urls = list(artifact_urls) + [asset_report.as_posix()]

    html = _render(
        artifact_urls,
        agent_results,
        metadata,
        changelog,
        feedback,
        meta_insights,
        self_improvement,
    )
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "summary.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    urls = json.loads(os.getenv("SUMMARY_ARTIFACTS", "[]"))
    agents = json.loads(os.getenv("SUMMARY_AGENTS", "{}"))
    feedback = os.getenv("SUMMARY_FEEDBACK", "")
    meta = os.getenv("SUMMARY_META", "")
    self_imp = os.getenv("SUMMARY_SELF", "")
    path = generate_summary(
        urls,
        agents,
        feedback,
        meta_insights=meta,
        self_improvement=self_imp,
    )
    print(path)


if __name__ == "__main__":
    main()
