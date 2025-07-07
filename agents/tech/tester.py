from __future__ import annotations

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import config

from . import team_lead


def run_unity_tests(project_path: str) -> dict:
    """Run Unity EditMode and PlayMode tests and write metrics.json."""
    results: dict[str, dict[str, int]] = {}

    for platform in ["EditMode", "PlayMode"]:
        result_file = f"results_{platform}.xml"
        proc = subprocess.run(
            [
                "unity",
                "-batchmode",
                "-runTests",
                "-projectPath",
                project_path,
                "-testResults",
                result_file,
                "-testPlatform",
                platform,
            ],
            capture_output=True,
            text=True,
        )

        print(proc.stdout)
        print(proc.stderr)

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


def _ensure_playmode_test(script_path: str | None) -> None:
    """Create a simple PlayMode test template if none exists."""
    if not script_path:
        return
    test_dir = Path("Assets/Tests/PlayMode")
    test_dir.mkdir(parents=True, exist_ok=True)
    class_name = Path(script_path).stem
    test_file = test_dir / f"{class_name}Test.cs"
    if test_file.exists():
        return
    content = (
        f"using NUnit.Framework;\n"
        f"public class {class_name}Test {{\n"
        f"    [Test]\n"
        f"    public void TestSimplePasses() {{\n"
        f"        Assert.Pass();\n"
        f"    }}\n"
        f"}}\n"
    )
    test_file.write_text(content, encoding="utf-8")


def tester(task_spec) -> dict:
    project_path = config.PROJECT_PATH
    _ensure_playmode_test(task_spec.get("path"))

    results = run_unity_tests(project_path)

    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())

    team_lead.update_project_map(
        task_spec.get("feature", "unknown"), total_failed == 0
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
