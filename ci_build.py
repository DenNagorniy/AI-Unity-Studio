import json
from pathlib import Path

import config
from agents.tech import build_agent
from utils.feature_index import load_index, update_feature


def main() -> None:
    if not Path(config.UNITY_CLI).exists():
        print(f"ERROR: Unity CLI not found at {config.UNITY_CLI}")
        return

    try:
        res = build_agent.run({"target": "WebGL"})
        status = "built" if res.get("status") == "success" else "failed"
    except Exception as e:  # noqa: PERF203
        res = {"error": str(e)}
        status = "failed"
    index = load_index()
    for feat in index.get("features", []):
        update_feature(feat.get("id", "unknown"), feat.get("name", ""), status)
    reports_dir = Path("ci_reports")
    reports_dir.mkdir(exist_ok=True)
    if res.get("artifact") and Path(res["artifact"]).exists():
        Path(res["artifact"]).rename(reports_dir / Path(res["artifact"]).name)
    for extra in ["build.log"]:
        if Path(extra).exists():
            Path(extra).rename(reports_dir / Path(extra).name)

    (reports_dir / "ci_build.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("Build reports saved to ci_reports/")


if __name__ == "__main__":
    main()
