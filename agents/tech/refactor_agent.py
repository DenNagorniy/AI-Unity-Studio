from __future__ import annotations

import subprocess

import config


def run(input: dict) -> dict:
    """Run Roslyn analyzers and check for dead code."""

    analyze_cmd = [
        "dotnet",
        "build",
        config.PROJECT_PATH,
        "/warnaserror",
        "/property:RunAnalyzers=true",
    ]
    proc = subprocess.run(analyze_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Roslyn analyzers failed: {proc.stderr.strip()}")

    dead_code = [
        line.strip()
        for line in proc.stdout.splitlines()
        if "warning" in line and "is never used" in line
    ]

    format_cmd = [
        "dotnet",
        "format",
        config.PROJECT_PATH,
        "--verify-no-changes",
    ]
    fmt_proc = subprocess.run(format_cmd, capture_output=True, text=True)
    if fmt_proc.returncode != 0:
        raise RuntimeError(f"dotnet format failed: {fmt_proc.stderr.strip()}")

    return {
        "returncode": proc.returncode or fmt_proc.returncode,
        "dead_code": dead_code,
        "stdout": (proc.stdout + fmt_proc.stdout)[:1000],
        "stderr": (proc.stderr + fmt_proc.stderr)[:1000],
    }
