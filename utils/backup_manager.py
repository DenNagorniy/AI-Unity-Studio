from __future__ import annotations

import os
import shutil
from pathlib import Path

BACKUP_ROOT = Path("_backups")


def _prepare_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_backup(feature_name: str, source_path: str) -> None:
    """Save a backup of ``source_path`` under ``feature_name``."""
    src = Path(source_path).resolve()
    dest = (Path.cwd() / BACKUP_ROOT / feature_name).resolve()

    # 💥 Явная проверка, чтобы dest не лежал внутри src
    if str(dest).startswith(str(src)):
        raise ValueError(f"Backup destination {dest} is inside source {src}. Cannot copy recursively.")

    _prepare_dir(dest.parent)

    if dest.exists():
        shutil.rmtree(dest)

    if src.is_dir():
        shutil.copytree(
            src,
            dest,
            ignore=shutil.ignore_patterns(
                BACKUP_ROOT.name,
                ".backup",
                ".git",
                "venv",
                "external",
                "__pycache__",
                "*.pyc",
                "*.pyo",
                "*.pyd",
            ),
            dirs_exist_ok=False,
        )
    elif src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    else:
        raise FileNotFoundError(f"Source path not found: {src}")

def restore_backup(feature_name: str, target_path: str) -> None:
    """Restore backup ``feature_name`` to ``target_path``."""
    src = Path.cwd() / BACKUP_ROOT / feature_name
    dest = Path(target_path)

    if not src.exists():
        raise FileNotFoundError(f'Backup for {feature_name} not found')

    if dest.exists():
        if dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest)

    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
