# Creative AI Team — Spec (v0)

## 🎯 Цель
Автоматизация креативной части разработки:
**лор → нарратив → core-loop → moodboard → передача в тех пайплайн**

## 🧠 Основные агенты
| Агент                    | Отвечает за                       | Артефакты                               |
|--------------------------|------------------------------------|-----------------------------------------|
| 🎮 GameDesignerAgent      | Core loop, мета-прогрессия        | `docs/core_loop.md`                    |
| 📖 NarrativeDesignerAgent | Сценарии, диалоги, выборы         | `narrative_events/*.json`              |
| 📚 LoreKeeperAgent        | База мира, факты                  | `lorebook.json`                        |
| 🎨 ArtMoodAgent           | Визуальный стиль, референсы       | `moodboards/*.png`                     |
| 🧠 CreativeOrchestrator   | Координация всех агентов          | `idea_spec.json`                       |

## 🔗 Мини-пайплайн
1️⃣ Orchestrator получает идею  
2️⃣ GameDesigner → core loop  
3️⃣ NarrativeDesigner → события, сцены  
4️⃣ LoreKeeper → факты в лор  
5️⃣ ArtMood → moodboard / палитра  
6️⃣ Orchestrator → формирует `task_spec` для инженеров  

## 📦 Артефакты
- `idea_spec.json` — итоговая спецификация
- `lorebook.json` — база фактов
- `narrative_events/*.json` — структура сцен
- `moodboards/*.png` — референсы

## 🌱 Roadmap

| Версия | Цель                              | Done-критерий                                      |
|---------|-----------------------------------|----------------------------------------------------|
| **v0.0** | MVP генерация core loop + лор     | core_loop.md + lorebook.json                       |
| **v0.1** | Narrative events + выборы         | narrative_events/*.json                            |
| **v0.2** | Moodboard + палитры               | moodboards/*.png                                   |
| **v0.3** | Связка с тех пайплайном           | idea_spec.json передаётся инженерным агентам       |
| **v0.4** | Human review + оценка идей        | ревью + ручное подтверждение идеи перед генерацией |
| **v0.5** | Creative dashboard                | web-дашборд для просмотра артефактов               |
