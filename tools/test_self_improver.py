import yaml
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from agents.analytics import self_improver  # noqa: E402


def test_self_improver_updates_config(tmp_path, monkeypatch):
    cfg = tmp_path / "pipeline_config.yaml"
    cfg.write_text("agents:\n  - SceneBuilderAgent\n  - RefactorAgent\n", encoding="utf-8")
    meta = tmp_path / "meta_insights.md"
    meta.write_text(
        "SKIP RefactorAgent for future runs\nPRIORITIZE SceneBuilderAgent for visuals\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    res = self_improver.run({"out_dir": str(tmp_path)})
    assert res["status"] == "success"
    backup = tmp_path / "pipeline_config.backup.yaml"
    assert backup.exists()
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    assert "RefactorAgent" not in data["agents"]
    assert data["agents"][0] == "SceneBuilderAgent"
    report = tmp_path / "self_improvement.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "SKIP RefactorAgent" in text
