from __future__ import annotations

"""Build the Unity project for a given target."""

import shutil
import subprocess
from pathlib import Path

import config
from utils.agent_journal import log_action, log_trace


def run(data: dict) -> dict:
    """Build the project for a given target using Unity CLI."""
    target = data.get("target", "WebGL")
    out_dir = Path("Build") / target
    log_action("BuildAgent", f"start {target}")
    cmd = [
        config.UNITY_CLI,
        "-batchmode",
        "-projectPath",
        str(Path(config.PROJECT_PATH).parent),
        "-buildTarget",
        target,
        "-quit",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    Path("build.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")

    artifact = str(out_dir.with_suffix(".zip"))
    if out_dir.exists():
        shutil.make_archive(out_dir.as_posix(), "zip", root_dir=out_dir)
        status = "success"
    else:
        status = "missing"

    log_action("BuildAgent", status)

    result = {"target": target, "artifact": artifact, "status": status}
    log_trace("BuildAgent", "run", data, result)
    return result
