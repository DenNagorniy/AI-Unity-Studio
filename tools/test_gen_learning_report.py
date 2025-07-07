import json
from pathlib import Path

from tools.gen_learning_report import generate_learning_report


def test_generate_learning_report(tmp_path, monkeypatch):
    memory = {
        "learning_log": {
            "CoderAgent": [
                {"hash": "1", "input": "req", "output": "out", "result": "success"},
                {"hash": "2", "input": "req2", "output": "oops", "result": "error"},
            ],
            "AutoFix:CoderAgent": [
                {"hash": "x", "input": "err", "output": "diff", "result": "success"}
            ],
        }
    }
    mem_file = tmp_path / "agent_memory.json"
    mem_file.write_text(json.dumps(memory, ensure_ascii=False), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    out = generate_learning_report(out_dir=tmp_path, memory_path=mem_file)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "CoderAgent" in html
