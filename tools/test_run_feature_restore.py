import importlib
import os
from pathlib import Path


def test_run_feature_restore_called(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
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

    run_all._run_feature("feat", "desc", False)

    assert called.get("restore") == ("feat", "MyScripts")
