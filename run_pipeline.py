import json
import sys
from pathlib import Path

from agents.tech.coder import coder
from agents.tech.project_manager import run as task_manager
from agents.tech.tester import run as run_tests
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
    apply_patch(patch)

    # 3. Тесты Unity CLI
    report = run_tests(task_spec)
    print("✅ Tester report:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["failed"]:
        raise SystemExit("❌ Тесты упали — почини код или перегенерируй запрос.")

    config_path = Path("config.json")
    if config_path.exists():
        with config_path.open() as f:
            config_data = json.load(f)
        print(json.dumps(config_data, indent=2))


if __name__ == "__main__":
    main()
