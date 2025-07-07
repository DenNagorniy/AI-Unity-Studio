import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from agents.tech import feature_inspector  # noqa: E402


def test_feature_inspector_pass(tmp_path, monkeypatch):
    project_map = {
        "schema_version": 1,
        "features": {
            "feat": {
                "name": "feat",
                "status": "done",
                "files": [
                    "Assets/Scripts/Feat.cs",
                    "Assets/Tests/FeatTest.cs",
                    "Assets/Scenes/Feat.unity",
                ],
                "assets": ["Assets/Textures/feat.png"],
                "created_by": "CoderAgent",
                "created_at": "2025-01-01T00:00:00Z",
                "tested": True,
                "depends_on": [],
                "deleted": False,
            }
        },
    }
    feature_index = {"schema_version": 1, "features": [{"id": "FT-1", "name": "feat", "status": "done"}]}
    catalog = {"assets": [{"path": "Assets/Textures/feat.png", "type": "png"}]}
    monkeypatch.chdir(tmp_path)
    Path("project_map.json").write_text(json.dumps(project_map), encoding="utf-8")
    Path("feature_index.json").write_text(json.dumps(feature_index), encoding="utf-8")
    Path("asset_catalog.json").write_text(json.dumps(catalog), encoding="utf-8")

    result = feature_inspector.run({"feature": "feat"})
    assert result["verdict"] == "Pass"
    report = Path("feature_inspection.md")
    assert report.exists()
    assert "Pass" in report.read_text(encoding="utf-8")
