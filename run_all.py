"""Run full pipeline: tests, build, publish and changelog."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

import yaml

import ci_assets
import ci_build
import ci_test
from agents.tech import feature_inspector
from agents.creative import lore_validator
import feature_review_panel
import run_pipeline
from auto_escalation import main as run_escalation
from ci_publish import _load_env
from ci_publish import main as publish_main
from notify import notify_all
from pipeline_optimizer import suggest_optimizations
from tools.gen_agent_stats import generate_agent_stats
from tools.gen_changelog import main as gen_changelog
from tools.gen_ci_overview import generate_ci_overview
from tools.gen_multifeature_summary import generate_multifeature_summary
from tools.gen_summary import generate_summary
from utils.agent_journal import read_entries
from utils.backup_manager import restore_backup, save_backup
from ci_revert import apply_emergency_patch, save_success_state
from utils.pipeline_config import load_config

STATUS_PATH = Path("pipeline_status.json")


def _load_pipeline() -> dict:
    if STATUS_PATH.exists():
        try:
            return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"features": {}, "multi": False}


def _save_pipeline(data: dict) -> None:
    STATUS_PATH.write_text(json.dumps(data), encoding="utf-8")


def _init_features(names: list[str], multi: bool) -> None:
    data = {"features": {}, "multi": multi}
    for n in names:
        data["features"][n] = {
            "status": "queued",
            "started": None,
            "ended": None,
            "duration": None,
            "summary_path": "",
            "agent_results": {},
            "is_multi": multi,
        }
    _save_pipeline(data)


def _update_feature(name: str, info: dict) -> None:
    data = _load_pipeline()
    feature = data.setdefault("features", {}).setdefault(name, {})
    feature.update(info)
    _save_pipeline(data)


ALL_AGENTS = [
    "GameDesignerAgent",
    "ProjectManagerAgent",
    "ArchitectAgent",
    "SceneBuilderAgent",
    "CoderAgent",
    "TesterAgent",
    "FeatureInspectorAgent",
    "ReviewAgent",
    "BuildAgent",
    "RefactorAgent",
]


def _apply_skip(base: list[str], flags: list[str]) -> list[str]:
    skip = {f.split("=")[1] for f in flags}
    mapped = {f"{name.capitalize()}Agent" for name in skip}
    return [a for a in base if a not in mapped]


def run_once(optimize: bool = False, feature_name: str = "single") -> tuple[Path, dict]:
    """Execute full CI pipeline for a feature."""
    cfg = load_config()

    agents = cfg.get("agents") or ALL_AGENTS
    if optimize:
        opt = suggest_optimizations("agent_trace.log", "agent_learning.json")
        agents = _apply_skip(agents, opt["skip_flags"])
        if opt["opt_notes"]:
            print(opt["opt_notes"])
        if opt["warn_flags"]:
            print("⚠ Possible skips:", ", ".join(opt["warn_flags"]))

    if os.getenv("SKIP_PIPELINE") != "1":
        run_pipeline.main(agents)

    reports = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports.mkdir(exist_ok=True)
    for name in ["review_report.md", "review_report.json"]:
        if Path(name).exists():
            shutil.copy(Path(name), reports / Path(name).name)

    ci_test.main()
    insp_result = feature_inspector.run({"feature": feature_name, "out_dir": str(reports)})
    desc = Path("core_loop.md").read_text(encoding="utf-8") if Path("core_loop.md").exists() else ""
    catalog = {}
    if Path("asset_catalog.json").exists():
        try:
            catalog = json.loads(Path("asset_catalog.json").read_text(encoding="utf-8"))
        except Exception:
            catalog = {}
    dialogues = ""
    narr_dir = Path("narrative_events")
    if narr_dir.exists():
        for p in narr_dir.glob("*.json"):
            dialogues += p.read_text(encoding="utf-8") + "\n"
    lore_result = lore_validator.run({
        "feature": feature_name,
        "description": desc,
        "assets": catalog.get("assets", []),
        "dialogues": dialogues,
        "out_dir": str(reports),
    })
    if cfg["steps"].get("build", True):
        ci_build.main()

    # Auto-escalation after tests and auto-fix phase
    run_escalation(out_dir=str(reports))

    # Apply rollback patch from TeamLead if present
    tl_patch = reports / "teamlead_patch.json"
    if tl_patch.exists():
        apply_emergency_patch(feature_name, str(tl_patch))

    review_result = feature_review_panel.run({"feature": feature_name, "out_dir": str(reports)})

    publish_status = "success"
    if cfg["steps"].get("publish", True):
        try:
            publish_main()
        except Exception as e:  # noqa: PERF203
            publish_status = "error"
            print(f"Publish failed: {e}")

    if cfg["steps"].get("qc", True):
        try:
            ci_assets.main()
        except Exception as e:  # noqa: PERF203
            print(f"Asset pipeline failed: {e}")

    gen_changelog()
    generate_agent_stats(out_dir=str(reports))

    lines = read_entries()
    summary_lines = [
        "# Final Summary",
        "",
        "## Agent log",
        *[f"- {entry}" for entry in lines[-20:]],
    ]
    agent_results = {}
    insp_status = "success" if insp_result.get("verdict") == "Pass" else "error"
    agent_results["FeatureInspectorAgent"] = insp_status
    lore_status = "success" if lore_result.get("status") == "LorePass" else "error"
    agent_results["LoreValidatorAgent"] = lore_status
    agent_results["AIReviewPanel"] = review_result.get("verdict", "accept")
    try:
        test_data = json.loads((reports / "ci_test.json").read_text(encoding="utf-8"))
        build_data = json.loads((reports / "ci_build.json").read_text(encoding="utf-8"))
        test_status = "error" if "error" in test_data else "success"
        build_status = "success" if build_data.get("status") == "success" else "error"
        agent_results["TesterAgent"] = test_status
        agent_results["BuildAgent"] = build_status
        summary_lines += [
            "",
            "## CI Results",
            f"- Tests: {test_status}",
            f"- Build: {build_status}",
            f"- Feature Inspection: {insp_result['verdict']}",
            f"- Lore Validation: {lore_result['status']}",
            f"- Review Panel: {review_result['verdict']}",
        ]
    except Exception:
        pass

    urls = []
    try:
        cfg = _load_env()
        artifacts = [p for p in reports.iterdir() if p.suffix in {".zip", ".apk"}]
        base = cfg["S3_ENDPOINT"].rstrip("/")
        urls = [f"{base}/{cfg['S3_BUCKET']}/{p.name}" for p in artifacts]
        if urls:
            summary_lines += ["", "## Artifacts", *[f"- {u}" for u in urls]]
    except Exception:
        pass

    summary_lines.append("")
    summary_lines.append(f"CHANGELOG: {Path('CHANGELOG.md').resolve()}")

    summary = "\n".join(summary_lines)
    Path("final_summary.md").write_text(summary + "\n", encoding="utf-8")
    shutil.copy("final_summary.md", reports / "final_summary.md")
    print(summary)

    agent_results["Publish"] = publish_status
    summary_path = generate_summary(urls, agent_results, out_dir=str(reports))
    print(f"Summary HTML: {summary_path}")

    generate_ci_overview(out_dir=str(reports))

    notify_all(str(summary_path), "CHANGELOG.md", urls)

    return summary_path, agent_results


def _run_feature(name: str, prompt: str, optimize: bool) -> dict:
    """Run pipeline for a single feature and return result info."""
    base_reports = Path("ci_reports")
    feature_dir = base_reports / name
    old_dir = os.getenv("CI_REPORTS_DIR")
    os.environ["CI_REPORTS_DIR"] = str(feature_dir)
    feature_dir.mkdir(parents=True, exist_ok=True)

    # Save backup of workspace before running the pipeline
    save_backup(name, ".")

    orig_ask = run_pipeline.ask_multiline
    run_pipeline.ask_multiline = lambda: prompt

    start = time.time()
    status = "success"
    _update_feature(name, {"status": "running", "started": start})
    try:
        summary, results = run_once(optimize, name)
    except (SystemExit, Exception) as e:  # noqa: PERF203
        print(f"Feature {name} failed: {e}")
        status = "error"
        results = {}
        summary = feature_dir / "summary.html"
        # Restore previous state if pipeline failed
        restore_backup(name, ".")
    finally:
        run_pipeline.ask_multiline = orig_ask
        if old_dir is None:
            os.environ.pop("CI_REPORTS_DIR", None)
        else:
            os.environ["CI_REPORTS_DIR"] = old_dir

    end_time = time.time()
    duration = round(end_time - start, 2)
    rel_summary = summary.relative_to(base_reports)
    _update_feature(
        name,
        {
            "status": "passed" if status == "success" else "failed",
            "ended": end_time,
            "duration": duration,
            "summary_path": rel_summary.as_posix(),
            "agent_results": results,
        },
    )

    if status == "success":
        save_success_state(name, ".")
    return {
        "name": name,
        "status": status,
        "time": duration,
        "summary": rel_summary.as_posix(),
    }


def main(optimize: bool = False, multi: str | None = None) -> None:
    """Execute pipeline for one or multiple features."""
    if not multi:
        name = "single"
        _init_features([name], False)
        start = time.time()
        _update_feature(name, {"status": "running", "started": start})
        try:
            summary, results = run_once(optimize, name)
            status = "passed"
        except Exception:
            status = "failed"
            results = {}
            summary = Path("ci_reports") / "summary.html"
        finally:
            end_t = time.time()
            dur = round(end_t - start, 2)
            rel = summary.relative_to(Path("ci_reports"))
            _update_feature(
                name,
                {
                    "status": status,
                    "ended": end_t,
                    "duration": dur,
                    "summary_path": rel.as_posix(),
                    "agent_results": results,
                },
            )
            if status == "passed":
                save_success_state(name, ".")
        return

    data = yaml.safe_load(Path(multi).read_text(encoding="utf-8")) or {}
    features = data.get("features", {})
    if not isinstance(features, dict):
        print("Invalid YAML format: expected 'features' mapping")
        return

    names = list(features.keys())
    _init_features(names, True)
    results = []
    start_all = datetime.utcnow()
    for fname, prompt in features.items():
        print(f"\n=== {fname} ===")
        results.append(_run_feature(fname, str(prompt), optimize))
    total_time = round((datetime.utcnow() - start_all).total_seconds(), 2)
    summary = generate_multifeature_summary("ci_reports", results, total_time)
    print(f"Multi summary: {summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full pipeline")
    parser.add_argument("--optimize", action="store_true", help="Use pipeline optimizer")
    parser.add_argument("--multi", help="Path to YAML with multiple features")
    args = parser.parse_args()
    main(optimize=args.optimize, multi=args.multi)
