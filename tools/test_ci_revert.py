import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import json  # noqa: E402
import ci_revert  # noqa: E402


def test_apply_emergency_patch(monkeypatch, tmp_path):
    patch = {"modifications": [{"path": "f.cs", "content": "c"}]}
    patch_file = tmp_path / "patch.json"
    patch_file.write_text(json.dumps(patch), encoding="utf-8")
    called = {"restore": False, "apply": False}
    monkeypatch.setattr(ci_revert, "restore_backup", lambda *a, **k: called.__setitem__("restore", True))
    monkeypatch.setattr(ci_revert, "apply_patch", lambda p: called.__setitem__("apply", True))
    assert ci_revert.apply_emergency_patch("feat", str(patch_file)) is True
    assert called["restore"] and called["apply"]


def test_save_success_state(monkeypatch):
    called = {}
    monkeypatch.setattr(ci_revert, "save_backup", lambda *a, **k: called.setdefault("saved", True))
    ci_revert.save_success_state("feat")
    assert called.get("saved") is True
