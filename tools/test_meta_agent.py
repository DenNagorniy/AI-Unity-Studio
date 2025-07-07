import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from meta_agent import MetaAgent


def test_meta_agent(tmp_path, monkeypatch):
    # prepare sample files
    mem = {
        "learning_log": {
            "CoderAgent": [
                {"result": "error"},
                {"result": "success"},
                {"result": "error"},
            ],
            "AutoFix:CoderAgent": [
                {"output": "fix1"},
                {"output": "fix1"},
                {"output": "fix2"},
            ],
        }
    }
    mem_file = tmp_path / "agent_memory.json"
    mem_file.write_text(json.dumps(mem), encoding="utf-8")

    journal = tmp_path / "agent_journal.log"
    journal.write_text("2024-01-01 [CoderAgent] start\n", encoding="utf-8")

    trace = tmp_path / "trace_report.jsonl"
    entries = [
        {
            "agent": "CoderAgent",
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T00:00:02",
        }
    ]
    with trace.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    feedback = tmp_path / "user_feedback_report.md"
    feedback.write_text(
        "# User Feedback Report\n\n| Variant | Rating | Comment | Reason |\n| A | 4 | ok | good |\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    agent = MetaAgent(out_dir=str(tmp_path))
    res = agent.run()
    assert res["status"] == "success"
    report = tmp_path / "meta_insights.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "CoderAgent" in text
