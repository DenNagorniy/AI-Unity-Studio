import subprocess


def commit_changes(message: str) -> bool:
    """Stage all changes and commit them if there is anything to commit."""

    subprocess.run(["git", "add", "."], check=True)

    diff_proc = subprocess.run([
        "git",
        "diff",
        "--cached",
        "--quiet",
    ])
    if diff_proc.returncode == 0:
        print("ℹ️  No changes to commit")
        return False

    subprocess.run(["git", "commit", "-m", message], check=True)
    print("✅ Изменения закоммичены")
    return True
