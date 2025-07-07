from utils import pipeline_config


def test_load_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = pipeline_config.load_config()
    assert cfg["steps"]["build"] is True
    assert cfg["steps"]["publish"] is True
    assert cfg["steps"]["qc"] is True


def test_load_custom(tmp_path, monkeypatch):
    cfg_path = tmp_path / "pipeline_config.yaml"
    cfg_path.write_text("steps:\n  build: false\n  qc: false\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    cfg = pipeline_config.load_config()
    assert cfg["steps"]["build"] is False
    assert cfg["steps"]["qc"] is False

