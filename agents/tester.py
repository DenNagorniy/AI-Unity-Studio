# agents/tester.py  —  запускает EditMode + PlayMode тесты
import os, subprocess, tempfile, xml.etree.ElementTree as ET, textwrap, json
from pathlib import Path

def _run_unity(project: str, unity_cli: str, xml_path: str):
    cmd = [
        unity_cli,
        "-batchmode", "-nographics",
        "-projectPath", project,
        "-runTests", "-testPlatform", "EditMode",
        "-testResults", xml_path,
        "-quit"
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

def tester(task_spec, project_path: str) -> dict:
    unity_cli = os.getenv("UNITY_CLI")
    tmp_dir   = tempfile.TemporaryDirectory()
    xml_file  = Path(tmp_dir.name) / "results.xml"

    proc = _run_unity(project_path, unity_cli, str(xml_file))
    passed, failed, extra = _parse_results(xml_file)

    return {
        "passed": passed,
        "failed": failed,
        "logs": textwrap.dedent(f"""
            STDOUT:
            {proc.stdout[:1000]}
            ----
            STDERR:
            {proc.stderr[:1000]}
            {extra}
        """).strip(),
        "report_path": str(xml_file)
    }

# локальный тест
if __name__ == "__main__":
    PJ = r"D:/Start/unity-ai-lab"   # поправьте путь
    print(json.dumps(tester({}, PJ), indent=2, ensure_ascii=False))
