import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import feature_review_panel  # noqa: E402


def test_review_panel_majority(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # All accept
    monkeypatch.setattr(feature_review_panel.feature_inspector, "run", lambda data: {"verdict": "Pass"})
    monkeypatch.setattr(feature_review_panel.lore_validator, "run", lambda data: {"status": "LorePass"})
    monkeypatch.setattr(feature_review_panel.refactor_agent, "run", lambda data: {"returncode": 0, "dead_code": []})
    monkeypatch.setattr(feature_review_panel.tester, "run", lambda data: {"failed": 0})

    res = feature_review_panel.run({"feature": "feat", "out_dir": str(tmp_path)})
    assert res["verdict"] == "accept"
    report = tmp_path / "review_verdict.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "Final Verdict:" in content

    # Needs revision case
    monkeypatch.setattr(feature_review_panel.feature_inspector, "run", lambda data: {"verdict": "Needs Fix"})
    res = feature_review_panel.run({"feature": "feat", "out_dir": str(tmp_path)})
    assert res["verdict"] == "needs_revision"

    # Block case
    monkeypatch.setattr(feature_review_panel.tester, "run", lambda data: {"failed": 1})
    res = feature_review_panel.run({"feature": "feat", "out_dir": str(tmp_path)})
    assert res["verdict"] == "block"
