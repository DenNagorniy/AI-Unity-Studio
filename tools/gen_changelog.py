"""Generate CHANGELOG.md from agent_journal.log grouped by agent."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

LOG_PATH = Path("agent_journal.log")
CHANGELOG_PATH = Path("CHANGELOG.md")
LINE_RE = re.compile(r"^(\S+) \[(.+?)\] (.+)$")


def parse_log() -> dict[str, list[str]]:
    entries: dict[str, list[str]] = defaultdict(list)
    if not LOG_PATH.exists():
        return entries
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        match = LINE_RE.match(line)
        if not match:
            continue
        timestamp, agent, message = match.groups()
        entries[agent].append(f"{timestamp} {message}")
    return entries


def render(entries: dict[str, list[str]]) -> str:
    lines = ["# Changelog"]
    for agent, messages in entries.items():
        lines.append(f"\n## {agent}")
        for msg in messages:
            lines.append(f"- {msg}")
    return "\n".join(lines) + "\n"


def main() -> None:
    entries = parse_log()
    text = render(entries)
    CHANGELOG_PATH.write_text(text, encoding="utf-8")
    print("CHANGELOG.md updated")


if __name__ == "__main__":
    main()
