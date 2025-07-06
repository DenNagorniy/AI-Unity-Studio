# orchestrator.py
"""
Мини-оркестратор спринта-0: проходит по всем агентам,
генерирует патч, проверяет сборку и запускает Unity-тесты.
"""
import sys
import json
from agents.tech import (
    game_designer,
    project_manager,
    architect_agent,
    coder,
    scene_builder_agent,
    tester,
    refactor_agent,
    team_lead,
)
from utils import apply_patch
from utils.dotnet_tools import run_dotnet_build
import config


def main(text: str):
    team_lead.log("🚀 Start AI pipeline")

    # 1️⃣ Гейм-дизайн
    feature = game_designer.run({"text": text})
    team_lead.log(f"🎮 Feature: {json.dumps(feature, ensure_ascii=False)}")

    # 2️⃣ Планирование
    tasks = project_manager.run(feature)
    team_lead.log(f"📋 Tasks: {json.dumps(tasks, ensure_ascii=False)}")

    # 3️⃣ Архитектура
    arch = architect_agent.run(tasks)
    team_lead.log(f"🧱 Architecture: {json.dumps(arch, ensure_ascii=False)}")

    # 4️⃣ Построение сцены / префабов (опционально)
    scene_result = scene_builder_agent.run(arch)
    team_lead.log(f"🎨 Scene result: {json.dumps(scene_result, ensure_ascii=False)}")

    # 5️⃣ Генерация кода
    patch = coder.run(tasks)
    team_lead.log(f"👨‍💻 Patch generated: {json.dumps(patch, ensure_ascii=False)[:120]}...")

    # 6️⃣ Применение патча
    apply_patch.apply_patch(patch)
    team_lead.log("✅ Patch applied & committed")

    # 7️⃣ Сборка проекта
    run_dotnet_build(config.PROJECT_PATH)
    team_lead.log("🛠 dotnet build completed")

    # 8️⃣ Unity тесты
    test_res = tester.run(tasks)
    team_lead.log(f"🧪 Tests: {test_res.get('passed', 0)}✓ / {test_res.get('failed', 0)}✗")

    # 9️⃣ Статический анализ
    refactor_agent.run({})
    team_lead.log("🧼 Refactor check completed")

    team_lead.log("🎉 Pipeline completed")


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello world feature"
    main(text)
