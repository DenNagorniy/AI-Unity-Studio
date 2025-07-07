
---

# 📂 `docs/AI_Unity_Agent_Pipeline_Tech_Spec.md`

```markdown
# AI Unity Agent Pipeline — Tech Spec (v0)

## 🎯 Цель
Автоматизация инженерного цикла Unity:
**текст → план → C#-код → тесты → билд → журналирование**

## ⚙ Стек
| Технология      | Версия       | Назначение                     |
|-----------------|-------------|--------------------------------|
| Python           | 3.11+        | агенты                         |
| Unity CLI        | 6000.0.40f1  | сборка, тесты                  |
| Ollama LLM       | API          | генерация C#                   |
| Git / GitPython  | —            | патчи, история                 |
| Pydantic         | 1.x / 2.x    | валидация `project_map.json`   |

## 🔗 Пайплайн (MVP v0)
1️⃣ `orchestrator.py` — текстовый запрос  
2️⃣ `GameDesignerAgent` — идея фичи  
3️⃣ `ProjectManagerAgent` — задачи, acceptance  
4️⃣ `ArchitectAgent` — структура кода  
5️⃣ `SceneBuilderAgent` — сцена, префабы  
6️⃣ `CoderAgent` — C# + git-patch  
7️⃣ `TesterAgent` — юнит + интеграционные тесты  
8️⃣ `BuildAgent` — билд WebGL/Android  
9️⃣ `TeamLeadAgent` — журнал, метрики  

## 📂 Артефакты
- `project_map.json` — карта фич
- `journal.json` — журнал действий
- `metrics.json` — показатели пайплайна
- `TestResults.xml` — Unity тесты
- `review_report.md` — отчёт статического анализа
- `ci_reports/` — собранные артефакты CI

## AssetCrafter
AssetCrafter генерирует текстуры, спрайты и простые модели по описанию. В основе
используются InvokeAI REST API и Blender CLI. Скрипт `ci_assets.py` запускается в
CI, сохраняет ассеты в папку `Assets`, формирует превью `*_preview.png` и
обновляет `asset_catalog.json`.

Пример запуска:
```bash
python ci_assets.py  # генерирует ассеты из asset_requests.json
```

## Agent Collaboration Layer
Агенты могут делиться промежуточными результатами через `agent_memory.py`.
Память включается флагом `--use-memory` у `run_pipeline.py`. Данные
сохраняются в `agent_memory.json` и доступны через функции `read`/`write`.

### AutoFix Phase
При сбое шага (код, тесты или билд) запускается автоисправление.
`auto_fix.py` вызывает профильного агента, сохраняет патч в `patches/` и
применяет его. Каждое действие логируется строкой вида:
`timestamp | AUTO_FIX | agent | status | description`.
Пример: `2025-07-07 14:32:01 | AUTO_FIX | Coder | success | fixed missing method`.


## 🛠 CLI
```bash
python tools/mapctl.py validate  # проверить project_map.json
python tools/mapctl.py summary   # краткая статистика
python tools/mapctl.py index    # обновить FeatureIndex.md
python ci_test.py               # запустить тесты в CI
python ci_build.py              # сборка проекта в CI
python run_all.py               # полный цикл
python agent_playground.py --repl   # интерактивный режим

### pipeline_config.yaml
Файл `pipeline_config.yaml` описывает этапы CI.

```yaml
steps:
  build: true
  publish: true
  qc: true
agents:
  - CoderAgent
  - TesterAgent
```
Можно отключать шаги или указать конкретных агентов.

## 📡 Dashboard API
```bash
python dashboard_api.py
```
GET http://localhost:8000/data

## 🌱 Tech Roadmap

| Версия | Цель                                  | Done-критерий                                    |
|---------|---------------------------------------|--------------------------------------------------|
| **v0.0** | MVP пайплайн                         | текст → план → C# → тесты → билд                 |
| **v0.1** | Индекс фич, базовый CI               | `FeatureIndex.md`, CI билд и тесты без сбоев     |
| **v0.2** | Журналирование + human review        | `journal.json` с полными записями + review flow |
| **v0.3** | RefactorAgent + static analysis      | автоматический Roslyn + dead code detection      |
| **v0.4** | Creative → Tech связка               | передача core_loop / narrative в тех пайплайн    |
| **v0.5** | Advanced CI/CD                       | Unity build + публикация артефактов              |
| **v0.6** | Feature dashboard                    | web-дашборд для просмотра `project_map` и журналов |
| **v0.7** | Multi-agent параллельная сборка      | Celery + очередь задач для агентов               |
| **v0.8** | Multi-platform build                 | сборка WebGL, Android, iOS                       |
| **v0.9** | Asset pipeline                       | интеграция импорта ассетов / префабов            |
| **v1.0** | Production-ready AI Studio           | полный цикл <30 мин, поддержка релиз-билдов      |
