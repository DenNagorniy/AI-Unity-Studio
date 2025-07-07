import json
import sys

from agents.coder import coder
from agents.task_manager import task_manager
from agents.tester import tester
from config import PROJECT_PATH
from utils.apply_patch import apply_patch


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

    # 2. Генерация патча
    patch = coder(task_spec)
    print("🛠️ Patch:")
    print(json.dumps(patch, indent=2, ensure_ascii=False))
    apply_patch(patch, str(PROJECT_PATH))

    # 3. Тесты Unity CLI
    report = tester(task_spec, str(PROJECT_PATH))
    print("✅ Tester report:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["failed"]:
        raise SystemExit("❌ Тесты упали — почини код или перегенерируй запрос.")

    config_data = {}
    with open("config.json") as f:
        config_data = json.load(f)

    print(json.dumps(config_data, indent=2))


if __name__ == "__main__":
    main()
