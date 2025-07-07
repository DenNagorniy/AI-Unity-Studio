import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from agents.creative import lore_validator  # noqa: E402


def test_lore_validator_mismatch(tmp_path, monkeypatch):
    lore_dir = tmp_path / "lore"
    lore_dir.mkdir()
    (lore_dir / "base.txt").write_text("King Eldor rules Aria", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    result = lore_validator.run(
        {
            "feature": "spaceship",
            "description": "A giant spaceship lands in Aria",
            "assets": [],
            "dialogues": "Captain: hello",
        }
    )
    assert result["status"] == "Mismatch"
    report = Path("lore_validation.md")
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "Mismatch" in text
