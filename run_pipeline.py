import json
import sys
from pathlib import Path

from agents.tech import architect_agent, build_agent, coder, game_designer, refactor_agent, review_agent, tester
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

    log_action("TeamLead", "pipeline start")

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

    # 4. Review
    review_agent.run({})

    # 5. Тесты
    report = tester.run(arch)
    log_action("TesterAgent", f"passed={report['passed']} failed={report['failed']}")
    if report["failed"]:
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
