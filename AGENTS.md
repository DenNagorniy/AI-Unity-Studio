# AI-Unity Studio — Agents Overview

## 👨‍💻 Engineering Agents

| Агент              | Роль                                        |
|--------------------|---------------------------------------------|
| GameDesignerAgent   | Формирует идею фичи, goal, mechanics        |
| ProjectManagerAgent | Делит фичу на задачи, задаёт acceptance     |
| ArchitectAgent      | Определяет структуру, asmdef, namespace     |
| SceneBuilderAgent   | Генерирует сцены, префабы                   |
| CoderAgent          | Пишет C# код, генерирует git-patch          |
| TesterAgent         | Запускает Unity CLI тесты, анализ JUnit     |
| RefactorAgent       | Roslyn анализ, форматирование               |
| BuildAgent          | Сборка WebGL / Android                      |
| TeamLeadAgent       | Оркестрация, журналирование, метрики        |
| AssetCrafter (v1.1) | Генерация ассетов, QC и каталог             |

### Status

* GameDesignerAgent — ready
* ProjectManagerAgent — ready
* ArchitectAgent — ready
* SceneBuilderAgent — ready
* CoderAgent — ready
* TesterAgent — ready
* RefactorAgent — ready
* ReviewAgent — ready, создаёт review_report.md
* BuildAgent — ready
* TeamLeadAgent — ready
* AssetCrafter — ready (v1.1)

## 🎨 Creative Agents

| Агент                  | Роль                                      |
|------------------------|-------------------------------------------|
| GameDesignerAgent       | Core loop, мета-прогрессия                |
| NarrativeDesignerAgent  | Диалоги, сцены, сюжет                     |
| LoreKeeperAgent         | База лора, факты                          |
| ArtMoodAgent            | Визуальный стиль, moodboard               |
| CreativeOrchestrator    | Координация креативных агентов            |

## 🌱 Development Roadmap

| Версия | Цель                                  |
|---------|---------------------------------------|
| v0.0    | MVP пайплайн: код + тесты + билд      |
| v0.1    | Индекс фич + CI                       |
| v0.2    | Журналирование + review flow          |
| v0.3    | Refactor + Roslyn                     |
| v0.4    | Creative → Tech связка                |
| v0.5    | Advanced CI/CD                        |
| v0.6    | Dashboard                             |
| v0.7    | Multi-agent очередь                   |
| v0.8    | Multi-platform билд                   |
| v0.9    | Asset pipeline                        |
| v1.0    | Production AI studio                  |

## Current Milestone

v1.0 released

## Tasks
- [ ] Улучшить логи пайплайна и детализировать ошибки
- [ ] Ввести fallback-билды (WebGL -> Android)
- [ ] Подключить GitHub Issues или Jira
- [ ] Настроить автоматическую публикацию билдов
- [ ] Перевести CI на GitHub Actions/GitLab CI
- [ ] Поддержать Desktop и iOS сборки
- [ ] Развить SceneBuilderAgent для генерации сцен
- [ ] Реализовать mini feature pack
- [ ] Создать веб-dashboard и REST API
- [ ] Подготовить распределённую работу агентов
- [ ] Сделать web-интерфейс и плагин Unity Editor
