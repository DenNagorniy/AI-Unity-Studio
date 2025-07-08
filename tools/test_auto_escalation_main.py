import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import auto_escalation  # noqa: E402


def test_auto_escalation_main(monkeypatch, tmp_path):
    fails = [{"agent": "CoderAgent", "stage": "Code", "count": 4, "exception": "e"}]
    monkeypatch.setattr(auto_escalation, "detect_repeated_failures", lambda: fails)
    monkeypatch.setattr(auto_escalation, "trigger_teamlead_analysis", lambda f: "ok")
    out = tmp_path / "report.md"
    monkeypatch.setattr(auto_escalation, "generate_report", lambda f, r, out_dir="ci_reports": out)
    res = auto_escalation.main(out_dir=str(tmp_path))
    assert res == out
