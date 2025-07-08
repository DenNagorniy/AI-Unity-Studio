from __future__ import annotations

import json
from pathlib import Path

from utils.agent_journal import log_action
from utils.apply_patch import apply_patch
from utils.backup_manager import restore_backup, save_backup


BACKUP_DIR = Path('_backups')


def save_success_state(feature_name: str, source: str = '.') -> None:
    """Save current workspace snapshot for the feature."""
    save_backup(feature_name, source)


def apply_emergency_patch(feature_name: str, patch_file: str) -> bool:
    """Restore last successful state and apply TeamLead patch."""
    path = Path(patch_file)
    if not path.exists():
        return False

    try:
        patch = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: PERF203
        print(f'Invalid patch: {exc}')
        return False

    try:
        restore_backup(feature_name, '.')
    except Exception as exc:  # noqa: PERF203
        print(f'Restore failed: {exc}')

    apply_patch(patch)
    log_action('CI', 'Emergency Patch')
    return True
