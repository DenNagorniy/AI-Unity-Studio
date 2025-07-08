import json

from tools.gen_agent_scores import generate_agent_scores


def test_generate_agent_scores(tmp_path, monkeypatch):
    journal = tmp_path / "agent_journal.log"
    journal.write_text(
        "\n".join(
            [
                "2024-01-01T00:00:00 [CoderAgent] start",
                "2024-01-01T00:00:01 | AUTO_FIX | CoderAgent | success | patch",
                "2024-01-01T00:00:02 [TeamLead] escalation CoderAgent",
                "2024-01-01T00:00:03 [SelfImproverAgent] Removed CoderAgent",
            ]
        ),
        encoding="utf-8",
    )

    memory = {
        "learning_log": {
            "CoderAgent": [
                {"result": "success"},
                {"result": "error"},
                {"result": "success"},
            ],
            "AutoFix:CoderAgent": [{"result": "success"}],
        }
    }
    mem_file = tmp_path / "agent_memory.json"
    mem_file.write_text(json.dumps(memory), encoding="utf-8")

    trace = tmp_path / "agent_trace.log"
    trace.write_text("", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    out = generate_agent_scores(
        out_dir=tmp_path,
        journal_path=journal,
        memory_path=mem_file,
        trace_path=trace,
        scores_path=tmp_path / "agent_scores.json",
    )
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "CoderAgent" in html
    data = json.loads((tmp_path / "agent_scores.json").read_text(encoding="utf-8"))
    assert "CoderAgent" in data
