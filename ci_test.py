import json
from pathlib import Path

import config
from agents.tech import tester
from utils.feature_index import load_index, update_feature


def main() -> None:
    if not Path(config.UNITY_CLI).exists():
        print(f"ERROR: Unity CLI not found at {config.UNITY_CLI}")
        return

    try:
        res = tester.run({})
        status = "done"
    except Exception as e:  # noqa: PERF203
        res = {"error": str(e)}
        status = "failed"
    index = load_index()
    for feat in index.get("features", []):
        update_feature(feat.get("id", "unknown"), feat.get("name", ""), status)
    reports_dir = Path("ci_reports")
    reports_dir.mkdir(exist_ok=True)
    for p in res.get("report_paths", []):
        if Path(p).exists():
            Path(p).rename(reports_dir / Path(p).name)

    (reports_dir / "ci_test.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
