# AI-Unity Agent System — краткий обзор

*Что делает система?*  
Преобразует текстовый запрос гейм-дизайнера в рабочую фичу Unity-проекта через связку AI-агентов.

**Ключевые возможности**
1. Генерация C#-кода (DeepSeek Code).  
2. Автоматическое планирование задач.  
3. Юнит- и интеграционные тесты Unity CLI.  
4. Сборка WebGL/Android в CI.  
5. Единая «карта проекта» (`project_map.json`).  

**Поток «идея → билд» (коротко)**
Запрос → GameDesignerAgent → ProjectManagerAgent → ArchitectAgent
→ CoderAgent / SceneBuilderAgent → Unity Tests → BuildAgent


**Детальные спецификации** см.  
- инженерная часть — *tech/AI_Unity_Agent_Pipeline_Tech_Spec.md*  
- креативная часть — *creative/Creative_AI_Team_Spec.md*
