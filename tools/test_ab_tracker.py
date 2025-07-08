import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import ab_tracker  # noqa: E402


def test_ab_tracker_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pm = {
        "schema_version": 1,
        "features": {"feat": {"variants": ["A", "B"]}},
    }
    Path("project_map.json").write_text(json.dumps(pm), encoding="utf-8")

    events = {
        "A": {"feature_used": 5, "step_completed": 4, "error_occurred": 1},
        "B": {"feature_used": 6, "step_completed": 5, "error_occurred": 0},
    }
    monkeypatch.setattr(ab_tracker, "_collect_events", lambda f, v: events)

    res = ab_tracker.run({"out_dir": str(tmp_path)})
    assert res["winners"]["feat"] == "B"
    assert (tmp_path / "ab_test_report.md").exists()
    data = json.loads((tmp_path / "ab_test_results.json").read_text(encoding="utf-8"))
    assert data["feat"]["A"]["feature_used"] == 5
