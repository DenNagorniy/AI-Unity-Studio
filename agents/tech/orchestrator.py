# orchestrator.py
"""
Мини-оркестратор спринта-0: проходит по stub-агентам,
генерирует патч и запускает Unity-тесты.
"""
import sys, json
from agents.tech import (
    game_designer,
    project_manager,
    coder,
    tester,
    team_lead,
)

def main(text: str):
    team_lead.log("Start pipeline")

    feature = game_designer.run({"text": text})
    team_lead.log(f"Feature: {feature}")

    tasks = project_manager.run(feature)
    team_lead.log(f"Tasks: {tasks}")

    patch = coder.coder(tasks["tasks"][0])        # DeepSeek-генерация
    team_lead.log(f"Patch generated: {json.dumps(patch)[:80]}...")

    test_res = tester.tester(tasks)               # теперь берёт пути из config.py
    team_lead.log(f"Tests result → {test_res['passed']}✓ / {test_res['failed']}✗")

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello world feature"
    main(text)
