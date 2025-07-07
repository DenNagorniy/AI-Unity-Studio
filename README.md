# AI-Unity Studio

**AI-Unity-Studio** — мультиагентная система, которая превращает текстовый запрос в рабочую игровую фичу Unity через полный цикл:
> текст → план → код → тесты → билд

## 🚀 Возможности
- Генерация C#-кода (DeepSeek Code).
- Автоматическое планирование задач (LLM).
- Юнит- и интеграционные тесты (Unity CLI).
- Сборка WebGL/Android в CI.
- Единая карта проекта: `project_map.json`.
- Интерактивный Playground для агентов `agent_playground.py`.

## 💡 Поток данных
Запрос → GameDesignerAgent → ProjectManagerAgent → ArchitectAgent →  
SceneBuilderAgent / CoderAgent → TesterAgent → BuildAgent → TeamLeadAgent → журналирование

## Агенты
| Агент | Краткая роль |
|-------|--------------|
| GameDesignerAgent | формирует фичу |
| ProjectManagerAgent | планирование задач |
| ArchitectAgent | структура кода |
| SceneBuilderAgent | сцены и префабы |
| CoderAgent | C# код |
| TesterAgent | тесты |
| BuildAgent | сборка |
| TeamLeadAgent | логирование |
| AssetCrafter (v1.1) | генерация ассетов |

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
python run_all.py  # полный цикл: пайплайн + тесты + билд + ассеты
python run_all.py --optimize  # пропустить быстрые шаги по истории
```

Пайплайн: GameDesigner → ProjectManager → Architect → SceneBuilder → Coder → Tester → Build → AssetCrafter → TeamLead.

Для запуска всего процесса и сохранения CI отчётов используйте `run_all.py`.

После успешного прогона в каталоге `ci_reports/` будут собраны отчёты тестов и
сборки, а файл `final_summary.md` содержит краткий итог всех агентов.

## 🎯 Пакетный режим (--multi)

`run_all.py` поддерживает генерацию нескольких фич за один запуск.
Список фич задаётся в YAML-файле формата:

```yaml
features:
  test_feature_1: "Создай зону с радиацией и мутантом"
  test_feature_2: "Добавь безопасный лагерь и торговца"
  test_feature_3: "Новая ловушка на локации с эффектами"
```

Запуск:

```bash
python run_all.py --multi features.yaml
```

Результаты каждой фичи сохраняются в `ci_reports/<feature>/`,
а общий отчёт — в `ci_reports/multifeature_summary.html`.

## Agent Playground

Для ручного взаимодействия с любым агентом используйте:

```bash
python agent_playground.py --agent CoderAgent --input '{"feature": "Jump"}'
python agent_playground.py --repl  # REPL-режим
```

## Shared Memory

Флаг `--use-memory` включает общую память между агентами. Модуль
`agent_memory.py` сохраняет данные в `agent_memory.json` и предоставляет
функции `read(key)` и `write(key, value)`.

```bash
python run_pipeline.py --use-memory
```

Ключи памяти по умолчанию:
`feature_description`, `tasks`, `architecture`, `scene`, `patch`.

## Уведомления CI

Для отправки уведомлений настройте переменные в `.env`:

```bash
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASS=yourpass
SLACK_URL=https://hooks.slack.com/services/XXX
TELEGRAM_TOKEN=bot-token
TELEGRAM_CHAT_ID=123456
```

После выполнения `run_all.py` итоговое сообщение будет отправлено на Email, Slack и Telegram, а также сохранено в `agent_journal.log`. Подробный трейс агентов записывается в `agent_trace.log`.

## Webhook API и мониторинг

Для интеграции со сторонними CI/CD системами предусмотрены простые HTTP сервисы.

### Запуск пайплайна

`ci_webhook.py` запускает сервер с одним методом `POST /trigger`. В запросе
нужно передать заголовок `X-Token` со значением из `WEBHOOK_TOKEN`. При
успешной проверке токена запускается скрипт `run_all.py` в отдельном процессе.
Порт сервера задаётся переменной `WEBHOOK_PORT`.

### Мониторинг

`ci_monitor.py` предоставляет методы `GET /status`, `GET /reports` и `GET /ci-status`.

- `/status` — текущий статус пайплайна из `pipeline_status.json`.
- `/reports` — список артефактов, а также пути к summary и `CHANGELOG.md`.
- `/ci-status` — JSON о прогрессе всех фич.

Для монитора используется порт из `MONITOR_PORT`.
Интерфейс наблюдения доступен на [http://localhost:8000/ci-status](http://localhost:8000/ci-status).
Он работает при запуске `run_all.py` с опцией `--multi`.

## Asset Pipeline

После публикации билда выполняются два шага по работе с ассетами:

- `asset_qc.py` проверяет размеры текстур, количество полигонов и положение pivot у моделей. Отчёт сохраняется в `asset_qc.json`.
- `asset_catalog.py` сканирует папку `Assets` и формирует `asset_manifest.json` со списком файлов и их размером.

Обе утилиты вызываются автоматически из `run_all.py`.

## Agent Learning Report

Скрипт `tools/gen_learning_report.py` анализирует файл `agent_memory.json` и
создаёт страницу `ci_reports/learning_report.html` c краткой статистикой по
агентам.

Пример строки отчёта:

```
Agent  Calls  Successes  Fixes  Example Prompt          Hint
Coder  12     10         2      "Создай MonoBehaviour"  "Использован шаблон BaseMono"
```

## Trace Report

`tools/gen_trace_report.py` анализирует `agent_trace.log` и создаёт страницу
`ci_reports/trace_report.html` с таблицей времени работы агентов и интерактивным
таймлайном. В отчёте также показываются рекомендации по флагам `--skip` для
повторного запуска пайплайна без уже успешных шагов.

## Agent Analytics Report

`tools/gen_agent_stats.py` объединяет логи `agent_journal.log`, `agent_memory.json`
и `agent_trace.log` и создаёт страницу `ci_reports/agent_stats.html` со статистикой
по каждому агенту.

Флаг `--optimize` у `run_all.py` использует эти данные и `agent_learning.json`
для автоматического пропуска стабильных агентов. Пример вывода:
`⚡ Сэкономим до 23 сек, если пропустить: Tester, ReviewAgent`.

## Лицензия

```makefile
License: Proprietary — All Rights Reserved
```

