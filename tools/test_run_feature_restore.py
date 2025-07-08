import importlib
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402


def test_run_feature_restore_called(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    import types
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
    sys.modules["run_pipeline"] = types.SimpleNamespace(ask_multiline=lambda: {}, main=lambda *a, **k: None)

    run_all = importlib.import_module("run_all")

    called = {}

    monkeypatch.setattr(run_all, "_update_feature", lambda *a, **k: None)
    def fail_run_once(*a, **k):
        raise Exception("boom")
    monkeypatch.setattr(run_all, "run_once", fail_run_once)
    monkeypatch.setattr(run_all, "save_success_state", lambda *a, **k: None)
    monkeypatch.setattr(run_all.run_pipeline, "ask_multiline", lambda: {})
    monkeypatch.setattr(run_all, "save_backup", lambda n, p: called.setdefault("save", (n, p)))
    monkeypatch.setattr(run_all, "restore_backup", lambda n, p: called.setdefault("restore", (n, p)))

    os.environ["UNITY_SCRIPTS_PATH"] = "MyScripts"
    os.environ["PROJECT_PATH"] = ""
    Path("MyScripts").mkdir(parents=True, exist_ok=True)

    run_all._run_feature("feat", "desc", False)

    assert called.get("restore") == ("feat", "MyScripts")


def test_run_feature_restore_skipped(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    import types
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
    sys.modules["run_pipeline"] = types.SimpleNamespace(ask_multiline=lambda: {}, main=lambda *a, **k: None)

    run_all = importlib.import_module("run_all")

    called = {}

    monkeypatch.setattr(run_all, "_update_feature", lambda *a, **k: None)

    def fail_unity(*a, **k):
        raise RuntimeError("Unity CLI returned 1 for EditMode: boom")

    monkeypatch.setattr(run_all, "run_once", fail_unity)
    monkeypatch.setattr(run_all, "save_success_state", lambda *a, **k: None)
    monkeypatch.setattr(run_all.run_pipeline, "ask_multiline", lambda: {})
    monkeypatch.setattr(run_all, "save_backup", lambda n, p: called.setdefault("save", (n, p)))
    monkeypatch.setattr(run_all, "restore_backup", lambda n, p: called.setdefault("restore", (n, p)))

    os.environ["UNITY_SCRIPTS_PATH"] = "MyScripts"
    os.environ["PROJECT_PATH"] = ""
    Path("MyScripts").mkdir(parents=True, exist_ok=True)

    run_all._run_feature("feat", "desc", False)

    assert "restore" not in called
