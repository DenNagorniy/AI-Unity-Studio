# config.py
#
# Храним пути и ключи в одном месте.
# Любой файл проекта теперь берёт настройки отсюда.
from pathlib import Path
import os
from dotenv import load_dotenv

# читаем .env (лежит в корне проекта)
load_dotenv()

PROJECT_PATH = r"D:/Start/unity-ai-lab"                # абсолютный путь
UNITY_CLI    = r"C:/Program Files/Unity/Hub/Editor/6000.0.40f1/Editor/Unity.exe"
OPENAI_API_KEY = "ollama"   

if not PROJECT_PATH:
    raise ValueError("❌ PROJECT_PATH не задан в .env")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не задан в .env")
