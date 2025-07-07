import argparse
import json
import sys
from pathlib import Path

import agent_learning
import agent_memory
from agents.tech import architect_agent, build_agent, coder, game_designer, refactor_agent, review_agent, tester
from agents.tech.project_manager import run as task_manager
from agents.tech.tester import run as run_tests
from auto_fix import auto_fix
from dashboard import main as show_dashboard
from utils.agent_journal import log_action
from utils.apply_patch import apply_patch
from utils.feature_index import update_feature


def ask_multiline() -> str:
    print("🚀 Вставь запрос. Напиши END на новой строке и Enter:")
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "END":
            break
        lines.append(line.rstrip("\n"))
    return "\n".join(lines).strip()


def main(agents: list[str] | None = None, use_memory: bool = False):
    if use_memory:
        agent_memory.enable()
    user_prompt = ask_multiline()
    if not user_prompt:
        print("❌ Пустой запрос — завершаю.")
        return

    if use_memory:
        hint = agent_learning.get_agent_hint("ProjectManagerAgent", user_prompt)
        if hint:
            print(f"💡 Hint for ProjectManagerAgent: {hint}")

    # 1. Разбивка запроса
    if not agents or "ProjectManagerAgent" in agents:
        try:
            task_spec = task_manager(user_prompt)
            agent_learning.record_interaction("ProjectManagerAgent", user_prompt, task_spec, "success")
        except Exception as e:  # noqa: PERF203
            agent_learning.record_interaction("ProjectManagerAgent", user_prompt, str(e), "error")
            raise
    else:
        task_spec = {}
    print("📋 Task-spec:")
    print(json.dumps(task_spec, indent=2, ensure_ascii=False))
    log_action("TeamLead", "pipeline start")

    # 2. Генерация патча
    if use_memory:
        hint = agent_learning.get_agent_hint("CoderAgent", task_spec)
        if hint:
            print(f"💡 Hint for CoderAgent: {hint}")
    patch = coder.run(task_spec)
    agent_learning.record_interaction("CoderAgent", task_spec, patch, "success")
    print("🛠️ Patch:")
    print(json.dumps(patch, indent=2, ensure_ascii=False))
    # 1. Идея фичи
    if not agents or "GameDesignerAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("GameDesignerAgent", user_prompt)
            if hint:
                print(f"💡 Hint for GameDesignerAgent: {hint}")
        try:
            feature = game_designer.run({"text": user_prompt})
            log_action("GameDesignerAgent", feature.get("feature", ""))
            agent_learning.record_interaction("GameDesignerAgent", user_prompt, feature, "success")
        except Exception as e:  # noqa: PERF203
            agent_learning.record_interaction("GameDesignerAgent", user_prompt, str(e), "error")
            raise
    else:
        feature = {"feature": user_prompt}

    # 2. Архитектура
    if not agents or "ArchitectAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("ArchitectAgent", feature)
            if hint:
                print(f"💡 Hint for ArchitectAgent: {hint}")
        try:
            arch = architect_agent.run(feature)
            log_action("ArchitectAgent", arch.get("path", ""))
            agent_learning.record_interaction("ArchitectAgent", feature, arch, "success")
        except Exception as e:  # noqa: PERF203
            agent_learning.record_interaction("ArchitectAgent", feature, str(e), "error")
            raise
    else:
        arch = feature

    # 3. Код
    if not agents or "CoderAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("CoderAgent", arch)
            if hint:
                print(f"💡 Hint for CoderAgent: {hint}")
        try:
            patch = coder.run(arch)
            log_action("CoderAgent", "patch generated")
            apply_patch(patch)
            agent_learning.record_interaction("CoderAgent", arch, patch, "success")
        except Exception as e:  # noqa: PERF203
            fix_result = auto_fix(feature.get("feature", ""), "CoderAgent", str(e))
            agent_learning.record_interaction("AutoFix", str(e), fix_result, "success" if fix_result else "error")
            patch = coder.run(arch)
            log_action("CoderAgent", "patch generated")
            apply_patch(patch)
            agent_learning.record_interaction("CoderAgent", arch, patch, "error")

    # 3. Тесты Unity CLI
    if not agents or "TesterAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("TesterAgent", task_spec)
            if hint:
                print(f"💡 Hint for TesterAgent: {hint}")
        report = run_tests(task_spec)
        print("✅ Tester report:")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        agent_learning.record_interaction("TesterAgent", task_spec, report, "success")
    # 4. Review
    if not agents or "ReviewAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("ReviewAgent", {})
            if hint:
                print(f"💡 Hint for ReviewAgent: {hint}")
        result = review_agent.run({})
        agent_learning.record_interaction("ReviewAgent", {}, result, "success")

    # 5. Тесты
    if not agents or "TesterAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("TesterAgent", arch)
            if hint:
                print(f"💡 Hint for TesterAgent: {hint}")
        try:
            report = tester.run(arch)
            if report["failed"]:
                raise RuntimeError("tests failed")
            agent_learning.record_interaction("TesterAgent", arch, report, "success")
        except Exception as e:  # noqa: PERF203
            fix_result = auto_fix(feature.get("feature", ""), "TesterAgent", str(e))
            agent_learning.record_interaction("AutoFix", str(e), fix_result, "success" if fix_result else "error")
            report = tester.run(arch)
            agent_learning.record_interaction("TesterAgent", arch, report, "error")
        log_action("TesterAgent", f"passed={report['passed']} failed={report['failed']}")
        if report["failed"]:
            update_feature("FT-unknown", feature.get("feature", ""), "failed")
            log_action("TeamLead", "tests failed")
            raise SystemExit("❌ Тесты упали")

    # 6. Сборка
    if not agents or "BuildAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("BuildAgent", {"target": "WebGL"})
            if hint:
                print(f"💡 Hint for BuildAgent: {hint}")
        try:
            build_info = build_agent.run({"target": "WebGL"})
            agent_learning.record_interaction("BuildAgent", {"target": "WebGL"}, build_info, "success")
        except Exception as e:  # noqa: PERF203
            fix_result = auto_fix(feature.get("feature", ""), "BuildAgent", str(e))
            agent_learning.record_interaction("AutoFix", str(e), fix_result, "success" if fix_result else "error")
            build_info = build_agent.run({"target": "WebGL"})
            agent_learning.record_interaction("BuildAgent", {"target": "WebGL"}, build_info, "error")
        log_action("BuildAgent", build_info.get("status", ""))

    # 7. Refactor
    if not agents or "RefactorAgent" in agents:
        if use_memory:
            hint = agent_learning.get_agent_hint("RefactorAgent", {})
            if hint:
                print(f"💡 Hint for RefactorAgent: {hint}")
        result = refactor_agent.run({})
        agent_learning.record_interaction("RefactorAgent", {}, result, "success")

    update_feature("FT-unknown", feature.get("feature", ""), "done")

    config_path = Path("config.json")
    if config_path.exists():
        with config_path.open() as f:
            config_data = json.load(f)
        print(json.dumps(config_data, indent=2))

    log_action("TeamLead", "pipeline finished")
    show_dashboard()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run agent pipeline")
    parser.add_argument("--use-memory", action="store_true", help="Enable shared memory")
    parser.add_argument("--agents", nargs="*", help="Subset of agents to run")
    args = parser.parse_args()
    main(args.agents, use_memory=args.use_memory)
