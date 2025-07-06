# agents/tester.py
"""
Запускает Unity EditMode-тесты, парсит JUnit-XML и возвращает статистику.
Использует пути из config.py, чтобы не хардкодить их внутри файла.
"""

from __future__ import annotations
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import textwrap
import json
from pathlib import Path
import config  # ← единый источник путей / настроек

# ---------- helpers -------------------------------------------------


def _run_unity(project_path: str, unity_cli: str, xml_path: str):
    """Запустить Unity CLI с параметрами тестов."""
    cmd = [
        unity_cli,
        "-batchmode", "-nographics",
        "-projectPath", project_path,
        "-runTests", "-testPlatform", "EditMode",
        "-testResults", xml_path,
        "-quit"
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def _parse_results(xml_file: Path):
    """Подсчитать Passed / Failed из JUnit-XML."""
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


# ---------- public API ----------------------------------------------


def tester(task_spec) -> dict:
    """
    Args:
        task_spec: dict со списком задач (пока не используется).
    Returns:
        dict {passed, failed, logs, report_path}
    """
    unity_cli = config.UNITY_CLI
    project_path = config.PROJECT_PATH
    tmp_dir = tempfile.TemporaryDirectory()
    xml_file = Path(tmp_dir.name) / "results.xml"

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


# локальный быстрый тест (запускать при необходимости)
if __name__ == "__main__":
    print(json.dumps(tester({}), indent=2, ensure_ascii=False))
