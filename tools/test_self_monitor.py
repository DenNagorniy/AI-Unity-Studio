import importlib.util
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "self_monitor",
    Path(__file__).resolve().parents[1] / "agents/analytics/self_monitor.py",
)
self_monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(self_monitor)


def test_self_monitor_report(tmp_path, monkeypatch):
    journal = tmp_path / "agent_journal.log"
    journal.write_text(
        "\n".join(
            [
                "2024-01-01T00:00:00 [CoderAgent] start",
                "2024-01-01T00:00:01 [CoderAgent] error",
                "2024-01-01T00:00:02 [CoderAgent] start",
                "2024-01-01T00:00:03 [TesterAgent] start",
                "2024-01-01T00:00:04 [TesterAgent] end",
                "2024-01-01 00:00:05 | AUTO_FIX | CoderAgent | success | patch",
            ]
        ),
        encoding="utf-8",
    )

    memory = {
        "learning_log": {
            "CoderAgent": [
                {"result": "error"},
                {"result": "success"},
            ],
            "TesterAgent": [{"result": "success"}],
            "AutoFix:CoderAgent": [{"result": "success"}],
        }
    }
    mem_file = tmp_path / "agent_memory.json"
    mem_file.write_text(json.dumps(memory), encoding="utf-8")

    trace = tmp_path / "agent_trace.log"
    entries = [
        {
            "agent": "CoderAgent",
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T00:00:02",
        },
        {
            "agent": "TesterAgent",
            "start_time": "2024-01-01T00:00:03",
            "end_time": "2024-01-01T00:00:04",
        },
    ]
    with trace.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    monkeypatch.chdir(tmp_path)
    agent = self_monitor.SelfMonitorAgent(out_dir=str(tmp_path))
    res = agent.run()
    assert res["status"] == "success"
    report = tmp_path / "self_monitor_report.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "Self-Monitoring Report" in text
    assert "CoderAgent" in text
    assert "TesterAgent" in text
