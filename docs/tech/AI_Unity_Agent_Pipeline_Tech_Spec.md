
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
8️⃣ `FeatureInspectorAgent` — проверка фичи
9️⃣ `LoreValidatorAgent` — сверка с лором
9.5 `AI Review Panel` — коллективный вердикт
9.6 `ABTrackerAgent` — анализ A/B-тестов
🔟 `BuildAgent` — билд WebGL/Android
1️⃣1 `TeamLeadAgent` — журнал, метрики

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

## FeatureInspectorAgent
FeatureInspectorAgent проверяет целостность сгенерированной фичи на основе `project_map.json`, `feature_index.json` и `asset_catalog.json`. Отчёт сохраняется в `ci_reports/<feature>/feature_inspection.md`. При ошибках в index добавляется метка `needs_fix`.

## LoreValidatorAgent
Проверяет совпадение новой фичи с базовым лором проекта. Читает тексты из каталога `lore/` и `lorebook.json`, сравнивает их с описанием и диалогами. Отчёт `lore_validation.md` кладётся в `ci_reports/<feature>/` и возвращает статус `LorePass` или `Mismatch`.

## ABTrackerAgent
ABTrackerAgent отслеживает варианты фич с ключом `variants` в `project_map.json` и собирает события использования. Данные сохраняются в `ab_test_results.json`, после чего формируется отчёт `ab_test_report.md` с победившим вариантом.

## Agent Collaboration Layer
Память включается флагом `--use-memory` у `run_pipeline.py`. Данные
сохраняются в `agent_memory.json` и доступны через функции `read`/`write`.

### AutoFix Phase
При сбое шага (код, тесты или билд) запускается автоисправление.
`auto_fix.py` вызывает профильного агента, сохраняет патч в `patches/` и
применяет его. Каждое действие логируется строкой вида:
`timestamp | AUTO_FIX | agent | status | description`.
Пример: `2025-07-07 14:32:01 | AUTO_FIX | Coder | success | fixed missing method`.

### Auto Escalation
Если один агент выдаёт более трёх ошибок подряд по одной фиче,
модуль `auto_escalation.py` фиксирует это в `agent_journal.log`,
вызывает `TeamLeadAgent` для анализа и генерирует отчёт
`ci_reports/autofailure_report.md`.

### CI Revert
После успешного CI-прогона рабочая копия сохраняется в
`.ci_backups/<feature>/`. Если автоисправление не помогло и TeamLeadAgent
выдал патч `teamlead_patch.json`, скрипт `ci_revert.py` восстанавливает
бэкап и применяет патч как Emergency Patch.

### Agent Learning
Агенты ведут блок `learning_log` в `agent_memory.json`.\
Каждая итерация сохраняет вход, выход и статус (`success` или `error`).\
Перед новым вызовом агент запрашивает подсказку через `get_agent_hint()` и может
использовать успешный шаблон из прошлого.

### Agent Learning Report
Отчёт `learning_report.html` генерируется скриптом
`tools/gen_learning_report.py` и показывает статистику обучений агентов.

Пример строки таблицы:

```
Agent  Calls  Successes  Fixes  Example Prompt          Hint
Coder  12     10         2      "Создай MonoBehaviour"  "Использован шаблон BaseMono"
```

### Trace Report
Файл `agent_trace.log` хранит подробный JSONL-трейс работы агентов. Скрипт
`tools/gen_trace_report.py` анализирует его и формирует страницу
`ci_reports/trace_report.html` с таймлайном вызовов и таблицей длительностей.
Из отчёта также извлекаются рекомендации по флагам `--skip` для повторного
запуска пайплайна без лишних шагов.
Модуль `pipeline_optimizer.py` объединяет статистику `agent_trace.log` и
`agent_learning.json` и предлагает пропустить стабильные шаги через флаг
`--optimize` у `run_all.py`.

### Agent Analytics Report
Страница `agent_stats.html` формируется скриптом `tools/gen_agent_stats.py` на
основе `agent_journal.log`, `agent_memory.json` и `agent_trace.log` и содержит
обобщённую статистику по вызовам агентов.


## 🛠 CLI
```bash
python tools/mapctl.py validate  # проверить project_map.json
python tools/mapctl.py summary   # краткая статистика
python tools/mapctl.py index    # обновить FeatureIndex.md
python ci_test.py               # запустить тесты в CI
python ci_build.py              # сборка проекта в CI
python run_all.py               # полный цикл
python run_all.py --optimize    # пропустить быстрые шаги
python ci_revert.py             # восстановление из бэкапа
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
