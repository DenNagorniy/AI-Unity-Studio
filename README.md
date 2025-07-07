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
python run_all.py  # полный цикл: пайплайн + тесты + билд
```

Пайплайн: GameDesigner → ProjectManager → Architect → SceneBuilder → Coder → Tester → Build → TeamLead.

Для запуска всего процесса и сохранения CI отчётов используйте `run_all.py`.

После успешного прогона в каталоге `ci_reports/` будут собраны отчёты тестов и
сборки, а файл `final_summary.md` содержит краткий итог всех агентов.

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

После выполнения `run_all.py` итоговое сообщение будет отправлено на Email, Slack и Telegram, а также сохранено в `agent_journal.log`.

## Webhook API и мониторинг

Для интеграции со сторонними CI/CD системами предусмотрены простые HTTP сервисы.

### Запуск пайплайна

`ci_webhook.py` запускает сервер с одним методом `POST /trigger`. В запросе
нужно передать заголовок `X-Token` со значением из `WEBHOOK_TOKEN`. При
успешной проверке токена запускается скрипт `run_all.py` в отдельном процессе.
Порт сервера задаётся переменной `WEBHOOK_PORT`.

### Мониторинг

`ci_monitor.py` предоставляет методы `GET /status` и `GET /reports`.

- `/status` — текущий статус пайплайна из `pipeline_status.json`.
- `/reports` — список артефактов, а также пути к summary и `CHANGELOG.md`.

Для монитора используется порт из `MONITOR_PORT`.

## Лицензия

```makefile
License: Proprietary — All Rights Reserved
```

