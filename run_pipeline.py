import json
import sys
from pathlib import Path

from agents.tech import architect_agent, build_agent, coder, game_designer, refactor_agent, review_agent, tester
from agents.tech.project_manager import run as task_manager
from agents.tech.tester import run as run_tests
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


def main():
    user_prompt = ask_multiline()
    if not user_prompt:
        print("❌ Пустой запрос — завершаю.")
        return

    # 1. Разбивка запроса
    task_spec = task_manager(user_prompt)
    print("📋 Task-spec:")
    print(json.dumps(task_spec, indent=2, ensure_ascii=False))
    log_action("TeamLead", "pipeline start")

    # 2. Генерация патча
    patch = coder.run(task_spec)
    print("🛠️ Patch:")
    print(json.dumps(patch, indent=2, ensure_ascii=False))
    # 1. Идея фичи
    feature = game_designer.run({"text": user_prompt})
    log_action("GameDesignerAgent", feature.get("feature", ""))

    # 2. Архитектура
    arch = architect_agent.run(feature)
    log_action("ArchitectAgent", arch.get("path", ""))

    # 3. Код
    patch = coder.run(arch)
    log_action("CoderAgent", "patch generated")
    apply_patch(patch)

    # 3. Тесты Unity CLI
    report = run_tests(task_spec)
    print("✅ Tester report:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # 4. Review
    review_agent.run({})

    # 5. Тесты
    report = tester.run(arch)
    log_action("TesterAgent", f"passed={report['passed']} failed={report['failed']}")
    if report["failed"]:
        raise SystemExit("❌ Тесты упали — почини код или перегенерируй запрос.")
        update_feature("FT-unknown", feature.get("feature", ""), "failed")
        log_action("TeamLead", "tests failed")
        raise SystemExit("❌ Тесты упали")

    # 6. Сборка
    build_info = build_agent.run({"target": "WebGL"})
    log_action("BuildAgent", build_info.get("status", ""))

    # 7. Refactor
    refactor_agent.run({})

    update_feature("FT-unknown", feature.get("feature", ""), "done")

    config_path = Path("config.json")
    if config_path.exists():
        with config_path.open() as f:
            config_data = json.load(f)
        print(json.dumps(config_data, indent=2))

    log_action("TeamLead", "pipeline finished")
    show_dashboard()


if __name__ == "__main__":
    main()
