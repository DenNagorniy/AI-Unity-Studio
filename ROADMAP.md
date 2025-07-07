# AI-Unity Studio Roadmap

## v1.1 — Minor Release: Stability & DevOps

### Stability
- Улучшение логов: детализация ошибок пайплайна (CI, build, test)
- Добавление fallback-механизмов при сборке (WebGL → Android)
- Интеграция с реальными issue-трекерами (GitHub Issues / Jira)

### DevOps
- Автоматическая публикация билдов (GitHub Pages, S3 и т.п.)
- Настройка CI на GitHub Actions или GitLab CI

### Платформы
- Desktop build (Windows/Mac)
- Предварительная подготовка iOS сборки

### Asset pipeline
- AssetCrafter agent integrated for asset generation pipeline

## v1.2 — Feature Expansion

### Творческий пайплайн
- SceneBuilderAgent генерирует полноценные сцены с примитивами и материалами
- Поддержка нескольких связанных фич (mini feature pack)

### Аналитика
- Веб-dashboard для просмотра feature index и журналов
- REST API для интеграции со сторонними инструментами

## v2.0 — Major Release: Production-grade AI Studio

- Multi-agent распределённая обработка (кластеры агентов)
- Интерактивный web-интерфейс для запуска пайплайна и управления фичами
- Поддержка внешних LLM (OpenAI, Ollama, DeepSeek API)
- Плагин для Unity Editor для вызова агентов напрямую

