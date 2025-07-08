import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import ci_test  # noqa: E402


def test_ci_test_main(monkeypatch, tmp_path):
    (tmp_path / "unity").write_text("cli")
    monkeypatch.setattr(ci_test.config, "UNITY_CLI", str(tmp_path / "unity"))
    result = {"report_paths": [str(tmp_path / "report.xml")]}
    monkeypatch.setattr(ci_test.tester, "run", lambda *a, **k: result)
    Path(result["report_paths"][0]).write_text("ok", encoding="utf-8")
    monkeypatch.setattr(ci_test, "notify_all", lambda *a, **k: None)
    monkeypatch.setattr(ci_test, "gen_changelog", lambda: None)
    monkeypatch.setattr(ci_test, "load_index", lambda: {"features": [{"id": "1", "name": "f"}]})
    updates = []
    monkeypatch.setattr(ci_test, "update_feature", lambda *a: updates.append(a))
    monkeypatch.chdir(tmp_path)
    ci_test.main()
    assert updates and updates[0][2] == "done"
    assert (tmp_path / "ci_reports" / "report.xml").exists()
