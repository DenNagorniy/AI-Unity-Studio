import json

from auto_escalation import detect_repeated_failures, generate_report


def test_detect_repeated_failures(tmp_path):
    memory = {
        "learning_log": {
            "CoderAgent": [
                {"hash": "h1", "result": "error"},
                {"hash": "h1", "result": "error"},
                {"hash": "h1", "result": "error"},
                {"hash": "h1", "result": "error"},
            ],
            "TesterAgent": [
                {"hash": "t1", "result": "success"},
                {"hash": "t2", "result": "error"},
                {"hash": "t2", "result": "error"},
            ],
        }
    }
    mem_file = tmp_path / "agent_memory.json"
    mem_file.write_text(json.dumps(memory, ensure_ascii=False), encoding="utf-8")

    fails = detect_repeated_failures(mem_file, threshold=3)
    assert len(fails) == 1
    assert fails[0]["agent"] == "CoderAgent"


def test_generate_report(tmp_path):
    failures = [
        {
            "agent": "CoderAgent",
            "stage": "Code",
            "count": 4,
            "exception": "SyntaxError",
        }
    ]
    out = generate_report(failures, "Check syntax", out_dir=tmp_path)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "CoderAgent" in text
    assert "SyntaxError" in text
