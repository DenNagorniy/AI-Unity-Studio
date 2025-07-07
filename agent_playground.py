from __future__ import annotations

import argparse
import json
from importlib import import_module

from utils.agent_journal import log_trace


def _snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append('_')
        out.append(ch.lower())
    return ''.join(out)


def load_agent(name: str):
    mod_name = _snake(name)
    for pkg in ("agents.tech", "agents.creative"):
        try:
            return import_module(f"{pkg}.{mod_name}")
        except ModuleNotFoundError:
            continue
    raise ValueError(f"Agent {name} not found")


def run_agent(name: str, payload: dict) -> dict:
    agent = load_agent(name)
    if not hasattr(agent, "run"):
        raise ValueError(f"Agent {name} has no run()")
    result = agent.run(payload)
    log_trace(name, "run", payload, result)
    return result


def repl() -> None:
    print("Agent Playground REPL. Type 'exit' to quit.")
    data: dict = {}
    while True:
        line = input("> ").strip()
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        if " " in line:
            name, rest = line.split(" ", 1)
            try:
                payload = json.loads(rest)
            except json.JSONDecodeError:
                print("Invalid JSON. Using empty dict.")
                payload = {}
        else:
            name, payload = line, data
        try:
            data = run_agent(name, payload)
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:  # noqa: PERF203
            print(f"Error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactively run agents")
    parser.add_argument("--agent", help="Agent name to run")
    parser.add_argument("--input", help="JSON payload")
    parser.add_argument("--repl", action="store_true", help="REPL mode")
    args = parser.parse_args()

    if args.repl:
        repl()
        return

    if not args.agent:
        parser.error("--agent required unless --repl")
    payload = json.loads(args.input) if args.input else {}
    result = run_agent(args.agent, payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
