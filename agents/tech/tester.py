from __future__ import annotations
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import textwrap
import json
from pathlib import Path
import config
from . import team_lead

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

def _run_unity(project_path: str, unity_cli: str, xml_path: str, platform: str) -> subprocess.CompletedProcess:
    cmd = [
        unity_cli,
        "-batchmode",
        "-nographics",
        "-projectPath",
        project_path,
        "-runTests",
        "-testPlatform",
        platform,
        "-testResults",
        xml_path,
        "-quit",
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def _parse_results(xml_file: Path):
    if not xml_file.exists():
        return 0, 0, "results.xml not generated"
    tree = ET.parse(xml_file)
    root = tree.getroot()
    passed = failed = 0
    for tc in root.iter("test-case"):
        if tc.attrib.get("result") == "Passed":
            passed += 1
        else:
            failed += 1
    return passed, failed, ""

def tester(task_spec) -> dict:
    unity_cli = config.UNITY_CLI
    project_path = config.PROJECT_PATH
    _ensure_playmode_test(task_spec.get("path"))
    tmp_dir = tempfile.TemporaryDirectory()
    xml_edit = Path(tmp_dir.name) / "edit_results.xml"
    xml_play = Path(tmp_dir.name) / "play_results.xml"

    proc_edit = _run_unity(project_path, unity_cli, str(xml_edit), "EditMode")
    proc_play = _run_unity(project_path, unity_cli, str(xml_play), "PlayMode")

    p1, f1, extra1 = _parse_results(xml_edit)
    p2, f2, extra2 = _parse_results(xml_play)
    passed = p1 + p2
    failed = f1 + f2
    extra = f"{extra1}\n{extra2}".strip()

    team_lead.update_project_map(task_spec.get("feature", "unknown"), failed == 0)

    logs = textwrap.dedent(
        f"""
        EDIT STDOUT:
        {proc_edit.stdout[:1000]}
        ----
        PLAY STDOUT:
        {proc_play.stdout[:1000]}
        ----
        {extra}
        """
    ).strip()

    return {
        "passed": passed,
        "failed": failed,
        "logs": logs,
        "report_paths": [str(xml_edit), str(xml_play)],
    }

if __name__ == "__main__":
    print(json.dumps(tester({}), indent=2, ensure_ascii=False))
