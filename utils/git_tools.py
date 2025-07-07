import subprocess
from pathlib import Path

from utils.agent_journal import read_entries


def commit_changes(message: str) -> bool:
    """Stage all changes and commit them if there is anything to commit."""
    update_changelog()
    subprocess.run(["git", "add", "."], check=True)

    diff_proc = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--quiet",
        ]
    )
    if diff_proc.returncode == 0:
        print("ℹ️  No changes to commit")
        return False

    subprocess.run(["git", "commit", "-m", message], check=True)
    print("✅ Изменения закоммичены")
    return True


def update_changelog() -> None:
    entries = read_entries()
    if not entries:
        return
    path = Path("CHANGELOG.md")
    lines = ["# Changelog", ""] + [f"- {e}" for e in entries]
    path.write_text("\n".join(lines), encoding="utf-8")
