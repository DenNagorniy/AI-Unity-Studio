from __future__ import annotations

import json
import subprocess
from pathlib import Path

import config
from utils.agent_journal import log_action


def run(_: dict | None = None) -> dict:
    """Run static checks for Python and C# code."""
    log_action("ReviewAgent", "start")

    flake = subprocess.run(["flake8"], capture_output=True, text=True)
    dotnet_fmt = subprocess.run(["dotnet", "format", config.PROJECT_PATH], capture_output=True, text=True)
    roslyn = subprocess.run([
        "dotnet",
        "build",
        config.PROJECT_PATH,
        "/warnaserror",
        "/property:RunAnalyzers=true",
    ], capture_output=True, text=True)

    report = {
        "flake8": flake.stdout + flake.stderr,
        "dotnet_format": dotnet_fmt.stdout + dotnet_fmt.stderr,
        "roslyn": roslyn.stdout + roslyn.stderr,
    }
    Path("review_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    if flake.returncode or dotnet_fmt.returncode or roslyn.returncode:
        log_action("ReviewAgent", "issues found")
        status = "failed"
    else:
        log_action("ReviewAgent", "clean")
        status = "success"

    return {"status": status, "report": "review_report.json"}
