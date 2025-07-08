import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from agents.tech import project_manager, scene_builder_agent  # noqa: E402


def test_project_manager_component_detection(monkeypatch):
    reply = {
        "tasks": [
            {"feature": "Add object to scene", "acceptance": ["FindObjectOfType"]},
            {"feature": "Base behaviour", "acceptance": ["inherits from"]},
            {"feature": "Config data", "acceptance": ["config asset"]},
            {"feature": "Utility helpers", "acceptance": ["helper utils"]},
        ]
    }
    monkeypatch.setattr(project_manager, "ask_mistral", lambda p: json.dumps(reply))
    res = project_manager.run({"feature": "zone"})
    tasks = res["tasks"]
    assert tasks[0]["component_type"] == "MonoBehaviour" and tasks[0]["attach_to_scene"]
    assert tasks[1]["component_type"] == "abstract"
    assert tasks[2]["component_type"] == "ScriptableObject"
    assert tasks[3]["component_type"] == "static"


def test_scene_builder_creates_scene(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = {"path": "Generated/RadiationZoneEffect.cs", "attach_to_scene": True}
    result = scene_builder_agent.run(data)
    scene_file = tmp_path / "Assets/Scenes/Generated/RadiationZoneEffect_Test.unity"
    assert scene_file.exists()
    assert Path(result["scene_path"]).resolve() == scene_file
    text = scene_file.read_text(encoding="utf-8")
    assert "Feature_RadiationZoneEffect" in text
