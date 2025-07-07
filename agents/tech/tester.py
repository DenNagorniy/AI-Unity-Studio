from __future__ import annotations

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import config
from utils.agent_journal import log_action
from utils.test_generation import generate_test_files

from . import team_lead


def run_unity_tests(project_path: str) -> dict:
    """Run Unity EditMode and PlayMode tests and write metrics.json."""
    results: dict[str, dict[str, int]] = {}

    for platform in ["EditMode", "PlayMode"]:
        result_file = f"results_{platform}.xml"
        proc = subprocess.run(
            [
                config.UNITY_CLI,
                "-batchmode",
                "-runTests",
                "-projectPath",
                project_path,
                "-testResults",
                result_file,
                "-testPlatform",
                platform,
                "-quit",
            ],
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Unity CLI returned {proc.returncode} for {platform}: {proc.stderr.strip()}")

        if not Path(result_file).exists():
            raise RuntimeError(f"Result file not found: {result_file}")

        tree = ET.parse(result_file)
        root = tree.getroot()
        passed = int(root.attrib.get("passed", 0))
        failed = int(root.attrib.get("failed", 0))
        skipped = int(root.attrib.get("skipped", 0))

        results[platform] = {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        }

        if failed > 0:
            raise RuntimeError(f"{platform} tests failed: {failed} failed")

    with open("metrics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results


def _ensure_playmode_test(script_path: str | None, namespace: str) -> None:
    """Create simple EditMode/PlayMode tests if none exist."""
    if not script_path:
        return

    class_name = Path(script_path).stem
    test_dir = Path("Assets/Tests/Generated")
    logic_path = test_dir / f"Test_{class_name}_Logic.cs"
    behaviour_path = test_dir / f"Test_{class_name}_Behaviour.cs"

    if logic_path.exists() and behaviour_path.exists():
        return

    mods = generate_test_files(script_path, namespace)
    for mod in mods:
        path = Path(mod["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(mod["content"], encoding="utf-8")


def tester(task_spec) -> dict:
    project_path = config.PROJECT_PATH
    _ensure_playmode_test(task_spec.get("path"), task_spec.get("namespace", "AIUnityStudio.Generated"))

    results = run_unity_tests(project_path)

    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_tests = total_passed + total_failed + sum(r["skipped"] for r in results.values())
    coverage = (total_passed / total_tests) * 100 if total_tests else 0
    log_action("TesterAgent", f"coverage={coverage:.1f}%")
    if coverage < 80:
        log_action("TesterAgent", "low coverage")
        raise RuntimeError(f"Coverage {coverage:.1f}% below threshold")

    team_lead.update_project_map(
        task_spec.get("feature", "unknown"),
        [task_spec["path"]] if task_spec.get("path") else [],
        total_failed == 0,
    )

    return {
        "passed": total_passed,
        "failed": total_failed,
        "logs": "",
        "report_paths": [f"results_{p}.xml" for p in results.keys()],
    }


def run(task_spec) -> dict:
    """Public wrapper used by the orchestrator."""
    return tester(task_spec)


if __name__ == "__main__":
    print(json.dumps(tester({}), indent=2, ensure_ascii=False))
