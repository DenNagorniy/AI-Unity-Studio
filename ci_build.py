import json
from agents.tech import build_agent
from utils.feature_index import update_feature, load_index


def main() -> None:
    try:
        res = build_agent.run({"target": "WebGL"})
        status = "built" if res.get("status") == "success" else "failed"
    except Exception as e:  # noqa: PERF203
        res = {"error": str(e)}
        status = "failed"
    index = load_index()
    for feat in index.get("features", []):
        update_feature(feat.get("id", "unknown"), feat.get("name", ""), status)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
