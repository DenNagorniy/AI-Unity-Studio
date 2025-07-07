"""Generate HTML summary for CI pipeline."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterable

from jinja2 import Environment

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Pipeline Summary</title>
<style>
  body { font-family: Arial, sans-serif; }
  table { border-collapse: collapse; }
  th, td { border: 1px solid #ccc; padding: 4px 8px; }
</style>
</head>
<body>
<h1>Pipeline Summary</h1>

<h2>Artifacts</h2>
<ul>
{% for url in artifact_urls %}
  <li><a href="{{ url }}">{{ url }}</a></li>
{% endfor %}
</ul>

<h2>Changelog</h2>
<pre>{{ changelog }}</pre>

<h2>Agent Results</h2>
<table>
<tr><th>Agent</th><th>Result</th></tr>
{% for name, result in agent_results.items() %}
<tr><td>{{ name }}</td><td>{{ result }}</td></tr>
{% endfor %}
</table>

<h2>Metadata</h2>
<ul>
  <li>Date: {{ metadata.date }}</li>
  <li>Commit: {{ metadata.git_commit }}</li>
  <li>User: {{ metadata.user }}</li>
</ul>

</body>
</html>
"""


def _render(
    artifact_urls: Iterable[str],
    agent_results: dict[str, str],
    metadata: dict[str, str],
    changelog: str,
) -> str:
    env = Environment()
    template = env.from_string(TEMPLATE)
    return template.render(
        artifact_urls=list(artifact_urls),
        agent_results=agent_results,
        metadata=metadata,
        changelog=changelog,
    )


def generate_summary(
    artifact_urls: list[str],
    agent_results: dict[str, str],
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

    html = _render(artifact_urls, agent_results, metadata, changelog)
    out_directory = Path(out_dir)
    out_directory.mkdir(exist_ok=True)
    out_path = out_directory / "summary.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    urls = json.loads(os.getenv("SUMMARY_ARTIFACTS", "[]"))
    agents = json.loads(os.getenv("SUMMARY_AGENTS", "{}"))
    path = generate_summary(urls, agents)
    print(path)


if __name__ == "__main__":
    main()
