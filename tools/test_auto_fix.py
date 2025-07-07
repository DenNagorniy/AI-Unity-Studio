import auto_fix
from utils import agent_journal


def test_auto_fix_creates_patch_and_logs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(agent_journal, "LOG_PATH", tmp_path / "log.log")

    patch = {"modifications": [{"path": "fix.txt", "content": "ok", "action": "overwrite"}]}
    monkeypatch.setattr(auto_fix.coder, "run", lambda data: patch)
    applied = []

    def fake_apply(p):
        applied.append(p)

    monkeypatch.setattr(auto_fix, "apply_patch", fake_apply)

    auto_fix.auto_fix("Feat", "CoderAgent", "SyntaxError")

    assert (tmp_path / "patches" / "Feat_CoderAgent.json").exists()
    assert applied and applied[0] == patch
    log_content = (tmp_path / "log.log").read_text(encoding="utf-8")
    assert "AUTO_FIX" in log_content
    assert "success" in log_content
