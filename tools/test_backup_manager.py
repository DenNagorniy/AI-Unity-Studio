from utils.backup_manager import save_backup, restore_backup
from pathlib import Path
import shutil


def test_save_and_restore(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src = Path('feature')
    src.mkdir()
    (src / 'file.txt').write_text('data', encoding='utf-8')
    sub = src / 'sub'
    sub.mkdir()
    (sub / 'inner.txt').write_text('123', encoding='utf-8')

    save_backup('feat', str(src))
    assert (Path('.ci_backups') / 'feat').exists()

    shutil.rmtree(src)
    restore_backup('feat', str(src))

    assert (src / 'file.txt').read_text(encoding='utf-8') == 'data'
    assert (src / 'sub' / 'inner.txt').read_text(encoding='utf-8') == '123'
