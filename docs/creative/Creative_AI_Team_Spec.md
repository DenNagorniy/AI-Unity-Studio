# Creative AI Team — Spec (v0)

## 1. Цель
Автоматизировать креативную часть: лор, нарратив, core-loop, визуальные рефы.

## 2. Ключевые агенты
| Агент | Отвечает за | Выход |
|-------|-------------|-------|
| 🎮 GameDesignerAgent | Core-loop, прогрессия | `core_loop.md` |
| 📖 NarrativeDesignerAgent | Сцены, диалоги, выборы | `narrative_events/*.json` |
| 📚 LoreKeeperAgent | База мира | `lorebook.json` |
| 🎨 ArtMoodAgent | Mood-board и палитры | `moodboards/` |
| 🧠 CreativeOrchestratorAgent | Координация, сбор идей | `idea_spec.json` |

## 3. Мини-pipeline
1. Orchestrator получает идею.  
2. GameDesigner формирует core-loop.  
3. NarrativeDesigner пишет сцену.  
4. LoreKeeper заносит факты в `lorebook.json`.  
5. ArtMoodAgent генерирует визуальные рефы.  
6. Orchestrator передаёт `task_spec` инженерной команде.

## 4. Артефакты
* `lorebook.json` — словарь мира.  
* `narrative_events/scene_*.json` — структура сцен.  
* `moodboards/*.png` — визуальные референсы.

*(Разделы «Оценка идей», «Human review», «Расширенные режимы» допишем позже.)*
