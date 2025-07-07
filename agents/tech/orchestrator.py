import json
import sys

import config
from agents.creative import creative_orchestrator
from agents.tech import (
    architect_agent,
    build_agent,
    coder,
    game_designer,
    project_manager,
    refactor_agent,
    scene_builder_agent,
    team_lead,
    tester,
)
from utils import apply_patch
from utils.dotnet_tools import run_dotnet_build


def main(text: str):
    team_lead.log("🚀 Start AI pipeline")

    creative_spec = creative_orchestrator.run({"text": text})
    team_lead.log(f"🎭 Creative spec: {json.dumps(creative_spec, ensure_ascii=False)}")

    feature = game_designer.run({"text": text})
    team_lead.log(f"🎮 Feature: {json.dumps(feature, ensure_ascii=False)}")

    tasks = project_manager.run(feature)
    team_lead.log(f"📋 Tasks: {json.dumps(tasks, ensure_ascii=False)}")

    arch = architect_agent.run(tasks)
    team_lead.log(f"🧱 Architecture: {json.dumps(arch, ensure_ascii=False)}")

    scene_result = scene_builder_agent.run(arch)
    team_lead.log(f"🎨 Scene result: {json.dumps(scene_result, ensure_ascii=False)}")

    patch = coder.run(arch)
    team_lead.log(f"👨‍💻 Patch generated: {json.dumps(patch, ensure_ascii=False)[:120]}...")

    apply_patch.apply_patch(patch)
    team_lead.log("✅ Patch applied & committed")

    build_stats = run_dotnet_build(config.PROJECT_PATH)
    team_lead.log("🛠 dotnet build completed")

    test_res = tester.run(tasks)
    team_lead.log(f"🧪 Tests: {test_res.get('passed', 0)}✓ / {test_res.get('failed', 0)}✗")

    build_info = build_agent.run({"target": "WebGL"})
    team_lead.log(f"📦 Build: {json.dumps(build_info, ensure_ascii=False)[:120]}...")

    ref_info = refactor_agent.run({})
    team_lead.log("🧼 Refactor check completed")

    metrics = {
        "tokens_used": 0,
        "compile_seconds": build_stats.get("seconds", 0),
        "tests_passed": test_res.get("passed", 0),
        "dead_warnings": len(ref_info.get("dead_code", [])),
    }
    team_lead.merge_feature(feature.get("feature", "unknown"), metrics)

    team_lead.log("🎉 Pipeline completed")


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello world feature"
    main(text)
