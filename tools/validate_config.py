from pipeline_config import get_config


def main() -> None:
    try:
        cfg = get_config()
    except Exception as e:
        print(f"❌ {e}")
        raise SystemExit(1)

    print("✅ Config valid")
    print(f"📁 Project path: {cfg['project_path']}")
    print(f"📂 Scripts path: {cfg['scripts_path']}")
    status = "present" if cfg.get('openai_api_key') else "missing"
    print(f"🧠 OpenAI Key: {status}")


if __name__ == "__main__":
    main()
