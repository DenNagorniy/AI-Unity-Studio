# Knowledge Base

## Особенности агентов
- Каждый инженерный агент выполняет одну фазу CI-процесса.
- Креативные агенты подготавливают лор и сцену перед кодом.

## Best practices
- Запускайте `run_all.py` для полного цикла с отчётами.
- Используйте `--multi` для пакетной генерации нескольких фич.
- Храните результаты в `ci_reports/` и обновляйте индексы после запуска.

## Шаблоны промтов
- `{"feature": "Jump"}` — для CoderAgent.
- `{"scene": "Battle"}` — для SceneBuilderAgent.

## Примеры успешных фич
- **test_feature** — базовый пример; отчёт `ci_reports/test_feature/summary.html`.
- **feature_alpha** — демонстрационный набор сцен; отчёт `ci_reports/feature_alpha/summary.html`.
- **inventory_system** — расширяемая система инвентаря (в разработке).
