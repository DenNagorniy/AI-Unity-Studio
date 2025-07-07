import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

import json  # noqa: E402
import yaml  # noqa: E402

import ci_repair  # noqa: E402


def test_repair_suggestion_and_auto_patch(tmp_path, monkeypatch):
    journal = tmp_path / "agent_journal.log"
    journal.write_text(
        "\n".join([
            "2024-01-01 [TesterAgent] error: fail1",
            "2024-01-01 [TesterAgent] error: fail2",
            "2024-01-01 [TesterAgent] error: fail3",
        ]),
        encoding="utf-8",
    )
    trace = tmp_path / "agent_trace.log"
    trace.write_text("", encoding="utf-8")
    memory = {
        "learning_log": {
            "TesterAgent": [
                {"result": "error", "hash": "x"},
                {"result": "error", "hash": "x"},
                {"result": "error", "hash": "x"},
            ]
        }
    }
    mem_path = tmp_path / "agent_memory.json"
    mem_path.write_text(json.dumps(memory), encoding="utf-8")

    cfg = tmp_path / "pipeline_config.yaml"
    cfg.write_text(
        "agents:\n  - TesterAgent\n  - RefactorAgent\n",
        encoding="utf-8",
    )

    reports = tmp_path / "ci_reports"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ci_repair, "JOURNAL_PATH", journal)
    monkeypatch.setattr(ci_repair, "TRACE_PATH", trace)
    monkeypatch.setattr(ci_repair, "MEMORY_PATH", mem_path)
    monkeypatch.setattr(ci_repair, "CONFIG_PATH", cfg)
    monkeypatch.setattr(ci_repair, "REPORTS_DIR", reports)

    ci_repair.main(feature="feat", auto_repair=True)

    content = (reports / "repair_suggestion.md").read_text(encoding="utf-8")
    assert "TesterAgent" in content
    assert "Перезапустить TesterAgent" in content

    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    assert "TesterAgent" not in data["agents"]
    assert "RefactorAgent" in data["agents"]
