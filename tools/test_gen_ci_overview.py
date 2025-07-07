import json
from pathlib import Path

from tools.gen_ci_overview import generate_ci_overview
import tools.gen_agent_stats as gen_stats


def test_generate_ci_overview(tmp_path, monkeypatch):
    status = {
        "features": {
            "feat": {
                "status": "passed",
                "started": 1.0,
                "ended": 2.0,
                "summary_path": "summary.html",
            }
        }
    }
    (tmp_path / "pipeline_status.json").write_text(json.dumps(status), encoding="utf-8")

    journal = tmp_path / "agent_journal.log"
    journal.write_text("2024-01-01T00:00:00 [CoderAgent] start\n", encoding="utf-8")

    memory = {"learning_log": {"CoderAgent": [{"result": "success"}]}}
    (tmp_path / "agent_memory.json").write_text(json.dumps(memory), encoding="utf-8")

    trace = tmp_path / "agent_trace.log"
    entry = {"agent": "CoderAgent", "start_time": "2024-01-01T00:00:00", "end_time": "2024-01-01T00:00:01"}
    trace.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    reports = tmp_path / "ci_reports"
    reports.mkdir()
    (reports / "summary.html").write_text("<html></html>", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gen_stats, "JOURNAL_PATH", journal)
    monkeypatch.setattr(gen_stats, "MEMORY_PATH", tmp_path / "agent_memory.json")
    monkeypatch.setattr(gen_stats, "TRACE_PATH", trace)
    out = generate_ci_overview(out_dir=reports)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "CI Overview" in html
    assert "CoderAgent" in html
