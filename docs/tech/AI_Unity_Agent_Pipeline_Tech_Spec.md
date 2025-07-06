# AI Unity Agent Pipeline — Tech Spec (v0)

## 1. Цель
Автоматизировать инженерный цикл разработки Unity-фич:
* текст → план → C#-код → тесты → билд.

## 2. Минимальный стек
| Технология | Версия | Назначение |
|------------|--------|-----------|
| Python | 3.11+ | агенты |
| Unity CLI | 2022.3 LTS | сборка и тесты |
| DeepSeek Code | API | генерация C# |
| Git / GitPython | — | патчи и история |
| Pydantic | — | валидация `project_map.json` |

## 3. MVP-пайплайн
1. **orchestrator.py** — принимает текст.  
2. **GameDesignerAgent** — формирует фичу.  
3. **ProjectManagerAgent** — задачи + acceptance.  
4. **CoderAgent** — C#-код → git-patch.  
5. **Unity CLI** — runTests (зелёный?).  
6. **TeamLeadAgent** — запоминает результат.

## 4. Основные артефакты
* `project_map.json` — карта фич.  
* `journal.json` — лог действий агентов.  
* `TestResults.xml` — отчёт Unity.

## 5. CLI-утилиты
* `tools/mapctl.py validate|summary` — проверка карты проекта.

*(Полный разделы “Роли агентов”, “Журналирование”, “CI” будут дополняться по мере разработки.)*
