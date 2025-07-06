# utils/dotnet_tools.py
import subprocess

def run_dotnet_build(project_path: str):
    print(f"🛠 Запуск dotnet build для {project_path}")
    result = subprocess.run(
        ["dotnet", "build", project_path],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("❌ dotnet build failed")
        print("STDOUT:", result.stdout[:1000])
        print("STDERR:", result.stderr[:1000])
        raise RuntimeError("dotnet build failed")
    else:
        print("✅ dotnet build success")
