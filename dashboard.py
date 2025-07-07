from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def main() -> None:
    try:
        with urlopen("http://localhost:8000/data") as resp:
            data = json.loads(resp.read().decode())
        features = {f["name"]: f for f in data.get("index", {}).get("features", [])}
        metrics = {}
    except URLError:
        features = {}
        if Path("project_map.json").exists():
            data = json.loads(Path("project_map.json").read_text(encoding="utf-8"))
            features = data.get("features", {})

        metrics = {}
        metrics_path = Path("metrics.json")
        if metrics_path.exists():
            entries = json.loads(metrics_path.read_text(encoding="utf-8"))
            if isinstance(entries, list) and entries:
                metrics = entries[-1]

    print("=== Pipeline Dashboard ===")
    if features:
        print("Features:")
        for name, feat in features.items():
            status = "✅" if feat.get("tested") else "❌"
            print(f"- {name}: {status}")
    if metrics:
        print("\nLatest metrics:")
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()