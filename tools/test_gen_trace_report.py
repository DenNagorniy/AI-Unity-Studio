import json

from tools.gen_trace_report import generate_trace_report


def test_generate_trace_report(tmp_path, monkeypatch):
    log = tmp_path / "agent_trace.log"
    entries = [
        {
            "agent": "CoderAgent",
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T00:00:02",
            "status": "success",
        },
        {
            "agent": "CoderAgent",
            "start_time": "2024-01-01T00:00:03",
            "end_time": "2024-01-01T00:00:05",
            "status": "success",
        },
        {
            "agent": "TesterAgent",
            "start_time": "2024-01-01T00:00:06",
            "end_time": "2024-01-01T00:00:10",
            "status": "error",
        },
    ]
    with log.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    monkeypatch.chdir(tmp_path)
    out = generate_trace_report(out_dir=tmp_path, log_path=log)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "CoderAgent" in html
    assert "--skip=coder" in html
