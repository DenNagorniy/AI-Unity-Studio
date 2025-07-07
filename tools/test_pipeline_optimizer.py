import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # noqa: E402

from pipeline_optimizer import suggest_optimizations  # noqa: E402


def test_suggest_optimizations(tmp_path):
    trace = Path(__file__).resolve().parent.parent / "fixtures" / "trace_sample.jsonl"
    learning = Path(__file__).resolve().parent.parent / "fixtures" / "learning_sample.json"

    result = suggest_optimizations(trace, learning)

    assert "--skip=coder" in result["skip_flags"]
    assert "--skip=review" in result["skip_flags"]
    assert "--skip=tester" in result["warn_flags"]
    assert "экономим" in result["opt_notes"].lower()
