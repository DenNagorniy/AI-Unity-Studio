import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import json  # noqa: E402
import types  # noqa: E402


def test_run_all_features_batch(tmp_path, monkeypatch):
    dummy = types.SimpleNamespace(main=lambda *a, **k: None)
    sys.modules["ci_assets"] = dummy
    sys.modules["ci_build"] = dummy
    sys.modules["ci_test"] = dummy
    sys.modules["ab_tracker"] = dummy
    sys.modules["feature_review_panel"] = types.SimpleNamespace(run=lambda *a, **k: {"verdict": "accept"})
    sys.modules["auto_escalation"] = types.SimpleNamespace(main=lambda *a, **k: None)
    sys.modules["ci_publish"] = types.SimpleNamespace(_load_env=lambda: {}, main=lambda *a, **k: None)
    sys.modules["notify"] = types.SimpleNamespace(notify_all=lambda *a, **k: None)
    sys.modules["pipeline_optimizer"] = types.SimpleNamespace(suggest_optimizations=lambda *a, **k: {"skip_flags": [], "warn_flags": [], "opt_notes": ""})
    sys.modules["tools.gen_agent_stats"] = types.SimpleNamespace(generate_agent_stats=lambda *a, **k: None)
    sys.modules["tools.gen_changelog"] = types.SimpleNamespace(main=lambda *a, **k: None)
    sys.modules["tools.gen_ci_overview"] = types.SimpleNamespace(generate_ci_overview=lambda *a, **k: Path("o"))
    sys.modules["tools.gen_multifeature_summary"] = types.SimpleNamespace(generate_multifeature_summary=lambda *a, **k: Path("multi"))
    sys.modules["tools.gen_summary"] = types.SimpleNamespace(generate_summary=lambda *a, **k: Path("s"))
    sys.modules["utils.agent_journal"] = types.SimpleNamespace(read_entries=lambda: [], log_action=lambda *a, **k: None, log_trace=lambda *a, **k: None)
    sys.modules["utils.backup_manager"] = types.SimpleNamespace(save_backup=lambda *a, **k: None, restore_backup=lambda *a, **k: None)
    sys.modules["agents.analytics.self_improver"] = types.SimpleNamespace(run=lambda *a, **k: {"report": "r"})
    sys.modules["agents.analytics.self_monitor"] = types.SimpleNamespace(SelfMonitorAgent=lambda **k: types.SimpleNamespace(run=lambda: {"report": "m"}))
    sys.modules["agents.analytics.user_feedback"] = types.SimpleNamespace(run=lambda *a, **k: {"status": "success", "report": "u"})
    sys.modules["agents.creative.lore_validator"] = types.SimpleNamespace(run=lambda *a, **k: {"status": "LorePass"})
    sys.modules["agents.tech.feature_inspector"] = types.SimpleNamespace(run=lambda *a, **k: {"verdict": "Pass"})
    sys.modules["ci_revert"] = types.SimpleNamespace(apply_emergency_patch=lambda *a, **k: None, save_success_state=lambda *a, **k: None)
    sys.modules["utils.pipeline_config"] = types.SimpleNamespace(load_config=lambda: {"steps": {}, "agents": []})
    sys.modules["run_pipeline"] = types.SimpleNamespace(ask_multiline=lambda: "", main=lambda *a, **k: None)

    import importlib
    run_all = importlib.import_module("run_all")

    batch_src = Path("features_batch.yaml")
    batch = tmp_path / "features_batch.yaml"
    batch.write_text(batch_src.read_text(encoding="utf-8"), encoding="utf-8")

    status_path = tmp_path / "pipeline_status.json"
    monkeypatch.setattr(run_all, "STATUS_PATH", status_path)
    monkeypatch.chdir(tmp_path)

    def fake_run_once(optimize=False, feature_name="single"):
        reports_dir = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
        reports_dir.mkdir(parents=True, exist_ok=True)
        summary = reports_dir / "summary.html"
        summary.write_text(feature_name, encoding="utf-8")
        return summary, {}

    monkeypatch.setattr(run_all, "run_once", fake_run_once)
    monkeypatch.setattr(run_all, "save_backup", lambda *a, **k: None)
    monkeypatch.setattr(run_all, "restore_backup", lambda *a, **k: None)
    monkeypatch.setattr(run_all, "save_success_state", lambda *a, **k: None)
    monkeypatch.setattr(run_all, "generate_multifeature_summary", lambda *a, **k: Path("multi"))

    run_all.main(multi=str(batch))

    data = json.loads(status_path.read_text(encoding="utf-8"))
    assert data["multi"] is True
    assert len(data["features"]) >= 3
    assert all(f["status"] == "passed" for f in data["features"].values())
