import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_PATH = os.getenv("PROJECT_PATH")
UNITY_CLI = os.getenv("UNITY_CLI")
UNITY_SCRIPTS_PATH = os.getenv("UNITY_SCRIPTS_PATH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PROJECT_PATH:
    raise ValueError("❌ PROJECT_PATH не задан в .env")
if not UNITY_CLI:
    raise ValueError("❌ UNITY_CLI не задан в .env")
if not UNITY_SCRIPTS_PATH:
    raise ValueError("❌ UNITY_SCRIPTS_PATH не задан в .env")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не задан в .env")
