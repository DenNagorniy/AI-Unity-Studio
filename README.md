# AI-Unity-Studio

**AI-Unity-Studio** — автоматизированная мультиагентная студия для разработки игр на Unity.  
Система превращает обычный текстовый запрос в рабочую игровую фичу через полный цикл:

> **текст → план → код → тесты → билд**

👉&nbsp;**Полная документация:** [docs/Index.md](docs/Index.md)

---

## Быстрый старт (спринт-0)

```bash
# Установить зависимости
pip install -r requirements.txt

# Скопировать .env.example и указать пути к Unity проекту и CLI
cp .env.example .env && edit .env

# Запустить оркестратор
python -m agents.tech.orchestrator "Hello world feature"

Пайплайн: GameDesigner → ProjectManager → Architect → SceneBuilder → Coder → Tester → TeamLead → Refactor.
