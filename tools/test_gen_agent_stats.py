import json

from tools.gen_agent_stats import generate_agent_stats


def test_generate_agent_stats(tmp_path, monkeypatch):
    journal = tmp_path / "agent_journal.log"
    journal.write_text(
        "2024-01-01T00:00:00 [CoderAgent] start\n"
        "2024-01-01T00:00:01 [CoderAgent] end\n"
        "2024-01-01T00:00:02 [TesterAgent] start\n",
        encoding="utf-8",
    )

    memory = {
        "learning_log": {
            "CoderAgent": [
                {"result": "success"},
                {"result": "error"}
            ],
            "TesterAgent": [
                {"result": "success"}
            ],
            "AutoFix:CoderAgent": [
                {"result": "success", "output": "diff"}
            ]
        }
    }
    mem_file = tmp_path / "agent_memory.json"
    mem_file.write_text(json.dumps(memory, ensure_ascii=False), encoding="utf-8")

    trace = tmp_path / "agent_trace.log"
    entries = [
        {
            "agent": "CoderAgent",
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T00:00:02",
            "status": "success",
        },
        {
            "agent": "TesterAgent",
            "start_time": "2024-01-01T00:00:03",
            "end_time": "2024-01-01T00:00:05",
            "status": "error",
        },
    ]
    with trace.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    monkeypatch.chdir(tmp_path)
    out = generate_agent_stats(out_dir=tmp_path, journal_path=journal, memory_path=mem_file, trace_path=trace)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "CoderAgent" in html
    assert "TesterAgent" in html
