from __future__ import annotations

import subprocess
from pathlib import Path

import config
from utils.agent_journal import log_action, log_trace


def run(input: dict) -> dict:
    """Run Roslyn analyzers and dotnet format, saving report to refactor_report.txt."""

    log_action("RefactorAgent", "start")

    analyze_cmd = [
        "dotnet",
        "build",
        config.PROJECT_PATH,
        "/warnaserror",
        "/property:RunAnalyzers=true",
    ]
    proc = subprocess.run(analyze_cmd, capture_output=True, text=True)
    dead_code = [line.strip() for line in proc.stdout.splitlines() if "warning" in line and "is never used" in line]

    format_cmd = ["dotnet", "format", config.PROJECT_PATH]
    fmt_proc = subprocess.run(format_cmd, capture_output=True, text=True)

    report_path = Path("refactor_report.txt")
    report_path.write_text(proc.stdout + fmt_proc.stdout, encoding="utf-8")

    if proc.returncode != 0 or fmt_proc.returncode != 0:
        log_action("RefactorAgent", "failed")
    else:
        log_action("RefactorAgent", "completed")

    result = {
        "returncode": proc.returncode or fmt_proc.returncode,
        "dead_code": dead_code,
        "report": str(report_path),
    }
    log_trace("RefactorAgent", "run", input, result)
    return result
