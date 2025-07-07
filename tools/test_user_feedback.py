import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from agents.analytics import user_feedback  # noqa: E402


def test_user_feedback_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ab_results = {"feat": {"A": {}, "B": {}}}
    (tmp_path / "ab_test_results.json").write_text(json.dumps(ab_results), encoding="utf-8")

    feedback = {"feat": [{"variant": "A", "rating": 5, "comment": "ok", "reason": "speed"}]}
    monkeypatch.setattr(user_feedback, "_generate_feedback", lambda data: feedback)

    res = user_feedback.run({"out_dir": str(tmp_path)})
    assert res["status"] == "success"
    report = tmp_path / "user_feedback_report.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "User Feedback Report" in text
    assert "A" in text
