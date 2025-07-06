from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
import config

def run(input: dict) -> dict:
    """Build the project for a given target using Unity CLI."""

    target = input.get("target", "WebGL")
    out_dir = Path("Build") / target
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

    artifact = str(out_dir.with_suffix(".zip"))
    if out_dir.exists():
        shutil.make_archive(out_dir.as_posix(), "zip", root_dir=out_dir)

    return {
        "target": target,
        "artifact": artifact,
        "stdout": proc.stdout[:1000],
        "stderr": proc.stderr[:1000],
    }
