from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from utils.agent_journal import log_action, log_trace
from utils.feature_index import load_index, save_index

PM_PATH = Path("project_map.json")
INDEX_PATH = Path("feature_index.json")
CATALOG_PATH = Path("asset_catalog.json")


def _load_json(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def run(data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Inspect generated feature and produce markdown report."""
    data = data or {}
    feature = data.get("feature", "unknown")
    out_dir = Path(data.get("out_dir", "."))

    log_action("FeatureInspectorAgent", f"start {feature}")

    pm = _load_json(PM_PATH)
    fmap = pm.get("features", {}).get(feature, {})
    files: List[str] = fmap.get("files", [])

    issues: List[str] = []
    if not files:
        issues.append("missing files entry in project_map")
    else:
        if not any(p.endswith(".cs") for p in files):
            issues.append("no C# code files")
        if not any("Tests" in p for p in files):
            issues.append("no test files")
        if not any(p.endswith(".unity") for p in files):
            issues.append("no scene files")
    if not fmap.get("assets"):
        issues.append("no assets listed")

    index = load_index()
    if not any(f.get("name") == feature for f in index.get("features", [])):
        issues.append("feature not in feature_index.json")

    catalog = _load_json(CATALOG_PATH)
    asset_count = len(catalog.get("assets", []))

    verdict = "Pass" if not issues else "Needs Fix"

    if verdict != "Pass":
        feats = index.setdefault("features", [])
        updated = False
        for f in feats:
            if f.get("name") == feature:
                f["label"] = "needs_fix"
                updated = True
                break
        if not updated:
            feats.append({"id": feature, "name": feature, "status": "todo", "label": "needs_fix"})
        save_index(index)

    md_lines = [
        "# Feature Inspection",
        "",
        f"**Feature:** {feature}",
        f"**Verdict:** {verdict}",
        "",
    ]
    if issues:
        md_lines.append("## Issues")
        md_lines += [f"- {i}" for i in issues]
    else:
        md_lines.append("No issues found.")
    md_lines += ["", f"Assets in catalog: {asset_count}"]

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "feature_inspection.md"
    report_path.write_text("\n".join(md_lines), encoding="utf-8")

    result = {"verdict": verdict, "issues": len(issues), "report": str(report_path)}
    log_trace("FeatureInspectorAgent", "run", data, result)
    return result
