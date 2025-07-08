import yaml
from pathlib import Path


def test_features_batch_format():
    data = yaml.safe_load(Path("features_batch.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict), "YAML root should be a mapping"
    assert "features" in data, "Missing 'features' section"
    features = data["features"]
    assert isinstance(features, dict), "'features' should be a mapping"
    for name, prompt in features.items():
        assert isinstance(name, str) and name
        assert isinstance(prompt, str) and prompt
