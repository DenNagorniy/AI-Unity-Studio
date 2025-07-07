# AI-Unity Studio

**AI-Unity-Studio** — мультиагентная система, которая превращает текстовый запрос в рабочую игровую фичу Unity через полный цикл:
> текст → план → код → тесты → билд

## 🚀 Возможности
- Генерация C#-кода (DeepSeek Code).
- Автоматическое планирование задач (LLM).
- Юнит- и интеграционные тесты (Unity CLI).
- Сборка WebGL/Android в CI.
- Единая карта проекта: `project_map.json`.

## 💡 Поток данных
Запрос → GameDesignerAgent → ProjectManagerAgent → ArchitectAgent →  
SceneBuilderAgent / CoderAgent → TesterAgent → BuildAgent → TeamLeadAgent → журналирование

## ⚙ Минимальный стек
| Технология      | Версия       | Назначение                     |
|-----------------|-------------|--------------------------------|
| Python           | 3.11+        | агенты                         |
| Unity CLI        | 6000.0.40f1  | сборка, тесты                  |
| Ollama LLM       | API          | генерация C#                   |
| Git / GitPython  | —            | патчи, история                 |
| Pydantic         | 1.x / 2.x    | валидация `project_map.json`   |

## 📝 Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env  # Указать свои пути в .env
python -m agents.tech.orchestrator "Hello world feature"
```

Пайплайн: GameDesigner → ProjectManager → Architect → SceneBuilder → Coder → Tester → Build → TeamLead.

## Лицензия

```makefile
License: Proprietary — All Rights Reserved
```

