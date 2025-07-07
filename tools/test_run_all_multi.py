import json
import os
import sys
import types
from pathlib import Path


def test_run_all_multi(tmp_path, monkeypatch):
    dummy = types.SimpleNamespace(main=lambda *a, **k: None)
    sys.modules["ci_assets"] = dummy
    sys.modules["ci_build"] = dummy
    sys.modules["ci_test"] = dummy
    sys.modules["auto_escalation"] = types.SimpleNamespace(main=lambda *a, **k: None)
    sys.modules["ci_publish"] = types.SimpleNamespace(_load_env=lambda: {}, main=lambda *a, **k: None)
    sys.modules["notify"] = types.SimpleNamespace(notify_all=lambda *a, **k: None)
    sys.modules["pipeline_optimizer"] = types.SimpleNamespace(
        suggest_optimizations=lambda *a, **k: {"skip_flags": [], "warn_flags": [], "opt_notes": ""}
    )
    sys.modules["tools.gen_agent_stats"] = types.SimpleNamespace(generate_agent_stats=lambda *a, **k: None)
    sys.modules["tools.gen_changelog"] = types.SimpleNamespace(main=lambda *a, **k: None)
    sys.modules["tools.gen_ci_overview"] = types.SimpleNamespace(generate_ci_overview=lambda *a, **k: Path("o"))
    sys.modules["tools.gen_multifeature_summary"] = types.SimpleNamespace(
        generate_multifeature_summary=lambda *a, **k: Path("multi")
    )
    sys.modules["tools.gen_summary"] = types.SimpleNamespace(generate_summary=lambda *a, **k: Path("s"))
    sys.modules["utils.agent_journal"] = types.SimpleNamespace(read_entries=lambda: [])
    sys.modules["utils.backup_manager"] = types.SimpleNamespace(
        save_backup=lambda *a, **k: None, restore_backup=lambda *a, **k: None
    )
    sys.modules["ci_revert"] = types.SimpleNamespace(
        apply_emergency_patch=lambda *a, **k: None, save_success_state=lambda *a, **k: None
    )
    sys.modules["utils.pipeline_config"] = types.SimpleNamespace(load_config=lambda: {"steps": {}, "agents": []})
    sys.modules["run_pipeline"] = types.SimpleNamespace(ask_multiline=lambda: "", main=lambda *a, **k: None)

    import importlib

    run_all = importlib.import_module("run_all")

    yaml_path = tmp_path / "batch.yaml"
    yaml_path.write_text("features:\n  feat1: A\n  feat2: B\n", encoding="utf-8")

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

    def fake_multi(out_dir, results, total_time):
        out = Path(out_dir) / "multifeature_summary.html"
        out.write_text("ok", encoding="utf-8")
        return out

    monkeypatch.setattr(run_all, "generate_multifeature_summary", fake_multi)

    run_all.main(multi=str(yaml_path))

    data = json.loads(status_path.read_text(encoding="utf-8"))
    assert data["multi"] is True
    assert set(data["features"].keys()) == {"feat1", "feat2"}
    assert all(f["status"] == "passed" for f in data["features"].values())
    assert (tmp_path / "ci_reports" / "multifeature_summary.html").exists()
