import sys
from pathlib import Path


def main() -> int:
    missing = []
    for path in Path('.').rglob('*'):
        if path.suffix == '.meta':
            if not path.with_suffix('').exists():
                missing.append(str(path))
        elif path.is_file() and not path.name.endswith('.meta'):
            meta = path.with_suffix(path.suffix + '.meta')
            if not meta.exists():
                missing.append(str(meta))
    if missing:
        print('Missing meta pairs:')
        for m in missing:
            print('  ' + m)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
