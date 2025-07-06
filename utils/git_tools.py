import subprocess


def commit_changes(message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    print("✅ Изменения закоммичены")
