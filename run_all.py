from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

import ab_tracker
import ci_assets
import ci_build
import ci_test
import feature_review_panel
import run_pipeline
from agents.analytics import self_improver, self_monitor, user_feedback
from agents.creative import lore_validator
from agents.tech import feature_inspector
from auto_escalation import main as run_escalation
from ci_publish import _load_env
from ci_publish import main as publish_main
from ci_revert import apply_emergency_patch, save_success_state
from meta_agent import MetaAgent
from notify import notify_all
from pipeline_optimizer import suggest_optimizations
from tools.gen_agent_scores import generate_agent_scores
from tools.gen_agent_stats import generate_agent_stats
from tools.gen_changelog import main as gen_changelog
from tools.gen_multifeature_summary import generate_multifeature_summary
from tools.gen_summary import generate_summary
from utils.agent_journal import read_entries
from utils.backup_manager import restore_backup, save_backup

STATUS_PATH = Path("pipeline_status.json")

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


def _apply_skip(base: list[str], flags: list[str]) -> list[str]:
    skip = {f.split("=")[1] for f in flags}
    mapped = {f"{name.capitalize()}Agent" for name in skip}
    return [a for a in base if a not in mapped]


def run_once(optimize: bool = False, feature_name: str = "single") -> tuple[Path, dict]:
    from utils.pipeline_config import load_config

    cfg = load_config()
    agents = cfg.get("agents") or ALL_AGENTS
    if optimize:
        opt = suggest_optimizations("agent_trace.log", "agent_learning.json")
        agents = _apply_skip(agents, opt["skip_flags"])

    if os.getenv("SKIP_PIPELINE") != "1":
        run_pipeline.main(agents)

    reports = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports.mkdir(exist_ok=True)
    for name in ["review_report.md", "review_report.json"]:
        if Path(name).exists():
            shutil.copy(Path(name), reports / name)

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
    for p in Path("narrative_events").glob("*.json") if Path("narrative_events").exists() else []:
        dialogues += p.read_text(encoding="utf-8") + "\n"

    lore_result = lore_validator.run(
        {
            "feature": feature_name,
            "description": desc,
            "assets": catalog.get("assets", []),
            "dialogues": dialogues,
            "out_dir": str(reports),
        }
    )

    if cfg["steps"].get("build", True):
        ci_build.main()

    run_escalation(out_dir=str(reports))
    if (reports / "teamlead_patch.json").exists():
        apply_emergency_patch(feature_name, str(reports / "teamlead_patch.json"))

    review_result = feature_review_panel.run({"feature": feature_name, "out_dir": str(reports)})
    ab_tracker.run({"out_dir": str(reports)})
    feedback_result = user_feedback.run({"out_dir": str(reports)})

    if cfg["steps"].get("publish", True):
        try:
            publish_main()
        except Exception as e:
            print(f"Publish failed: {e}")

    if cfg["steps"].get("qc", True):
        try:
            ci_assets.main()
        except Exception as e:
            print(f"Asset pipeline failed: {e}")

    gen_changelog()
    generate_agent_stats(out_dir=str(reports))
    scores_path = generate_agent_scores(out_dir=str(reports))

    summary_lines = ["# Final Summary", "", "## Agent log", *[f"- {entry}" for entry in read_entries()[-20:]]]
    agent_results = {
        "FeatureInspectorAgent": "success" if insp_result.get("verdict") == "Pass" else "error",
        "LoreValidatorAgent": "success" if lore_result.get("status") == "LorePass" else "error",
        "AIReviewPanel": review_result.get("verdict", "accept"),
        "UserFeedbackAgent": feedback_result.get("status", "success"),
    }

    try:
        test_data = json.loads((reports / "ci_test.json").read_text())
        build_data = json.loads((reports / "ci_build.json").read_text())
        agent_results["TesterAgent"] = "error" if "error" in test_data else "success"
        agent_results["BuildAgent"] = "success" if build_data.get("status") == "success" else "error"
    except Exception:
        pass

    urls = []
    try:
        cfg = _load_env()
        base = cfg["S3_ENDPOINT"].rstrip("/")
        urls = [f"{base}/{cfg['S3_BUCKET']}/{p.name}" for p in reports.iterdir() if p.suffix in {".zip", ".apk"}]
    except Exception:
        pass

    summary_lines += ["", "## Artifacts", *[f"- {u}" for u in urls], "", f"CHANGELOG: {Path('CHANGELOG.md').resolve()}"]
    Path("final_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    shutil.copy("final_summary.md", reports / "final_summary.md")

    try:
        meta_result = MetaAgent(out_dir=str(reports)).run()
        feedback_text = Path(feedback_result["report"]).read_text()
        meta_text = Path(meta_result["report"]).read_text()
        self_result = self_improver.run({"out_dir": str(reports)})
        self_text = Path(self_result["report"]).read_text()
        monitor_result = self_monitor.SelfMonitorAgent(out_dir=str(reports)).run()
        monitor_path = monitor_result["report"]
    except Exception:
        feedback_text = meta_text = self_text = monitor_path = ""

    summary_path = generate_summary(
        urls,
        agent_results,
        feedback_text,
        meta_insights=meta_text,
        self_improvement=self_text,
        self_monitor=monitor_path,
        agent_scores=scores_path.as_posix(),
        out_dir=str(reports),
    )

    notify_all(str(summary_path), "CHANGELOG.md", urls)
    return summary_path, agent_results


def _run_feature(name: str, prompt: str | dict, optimize: bool) -> dict:
    base_reports = Path("ci_reports")
    feature_dir = base_reports / name
    os.environ["CI_REPORTS_DIR"] = str(feature_dir)
    feature_dir.mkdir(parents=True, exist_ok=True)

    scripts_path = os.getenv("UNITY_SCRIPTS_PATH", "Assets/Scripts")
    save_backup(name, scripts_path)

    orig_ask = run_pipeline.ask_multiline
    run_pipeline.ask_multiline = lambda: prompt if isinstance(prompt, dict) else {"feature": prompt}

    start = time.time()
    status = "success"
    _update_feature(name, {"status": "running", "started": start})
    try:
        summary, results = run_once(optimize, name)
    except Exception as e:
        print(f"Feature {name} failed: {e}")
        status = "error"
        results = {}
        summary = feature_dir / "summary.html"
        restore_backup(name, scripts_path)
    finally:
        run_pipeline.ask_multiline = orig_ask

    duration = round(time.time() - start, 2)
    rel_summary = summary.relative_to(base_reports)
    _update_feature(
        name,
        {
            "status": "passed" if status == "success" else "failed",
            "ended": time.time(),
            "duration": duration,
            "summary_path": rel_summary.as_posix(),
            "agent_results": results,
        },
    )

    if status == "success":
        save_success_state(name, ".")
    return {"name": name, "status": status, "time": duration, "summary": rel_summary.as_posix()}


def main(optimize: bool = False, multi: str | None = None) -> None:
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
    if not isinstance(data, dict) or "features" not in data:
        print("Invalid YAML format: expected 'features' mapping")
        sys.exit(1)
    features = data["features"]
    _init_features(list(features.keys()), True)

    results = []
    start_all = datetime.now(timezone.utc)
    for fname, prompt in features.items():
        print(f"\n=== {fname} ===")
        results.append(_run_feature(fname, prompt, optimize))
    total_time = round((datetime.now(timezone.utc) - start_all).total_seconds(), 2)
    summary = generate_multifeature_summary("ci_reports", results, total_time)
    print(f"Multi summary: {summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full pipeline")
    parser.add_argument("--optimize", action="store_true", help="Use pipeline optimizer")
    parser.add_argument("--multi", help="Path to YAML with multiple features")
    args = parser.parse_args()
    main(optimize=args.optimize, multi=args.multi)
