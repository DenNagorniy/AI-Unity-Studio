import subprocess
import time

def run_dotnet_build(project_path: str) -> dict:
    """Run dotnet build and return timing and output."""
    print(f"🛠 Запуск dotnet build для {project_path}")
    start = time.time()
    result = subprocess.run(
        ["dotnet", "build", project_path],
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start
    if result.returncode != 0:
        print("❌ dotnet build failed")
        print("STDOUT:", result.stdout[:1000])
        print("STDERR:", result.stderr[:1000])
        raise RuntimeError("dotnet build failed")
    else:
        print("✅ dotnet build success")
    return {"seconds": elapsed, "stdout": result.stdout[:1000]}
