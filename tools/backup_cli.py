import argparse
from utils.backup_manager import save_backup, restore_backup, BACKUP_ROOT
from pathlib import Path


def list_backups(feature: str) -> None:
    path = BACKUP_ROOT / feature
    if not path.exists():
        print(f"No backups for {feature}")
        return
    backups = sorted(path.iterdir(), reverse=True)
    for b in backups:
        print(b.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage backups for AI Unity Studio")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save = subparsers.add_parser("save")
    save.add_argument("feature", help="Name of the feature")
    save.add_argument("--src", default=".", help="Source path to back up")

    restore = subparsers.add_parser("restore")
    restore.add_argument("feature", help="Name of the feature")
    restore.add_argument("--target", default=".", help="Target path to restore")

    list_ = subparsers.add_parser("list")
    list_.add_argument("feature", help="Feature to list backups for")

    args = parser.parse_args()

    if args.command == "save":
        save_backup(args.feature, args.src)
    elif args.command == "restore":
        restore_backup(args.feature, args.target)
    elif args.command == "list":
        list_backups(args.feature)
