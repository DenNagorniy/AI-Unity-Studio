"""Utility functions to run agents with retry and skip support."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict

# Type alias for agent callable
default_input_type = Dict[str, Any]
AgentCallable = Callable[[default_input_type], default_input_type]


def run_with_retry(
    agent: AgentCallable,
    payload: default_input_type,
    *,
    retries: int = 3,
    delay: float = 1.0,
    skip_on_fail: bool = True,
) -> default_input_type:
    """Run an agent with retry logic.

    Args:
        agent: Callable that accepts a dictionary and returns a dictionary.
        payload: Input payload for the agent.
        retries: Number of attempts before giving up.
        delay: Delay in seconds between attempts.
        skip_on_fail: If True, return a skipped result when all retries fail
            instead of raising the exception.

    Returns:
        Dictionary result from the agent or skipped result.
    """

    attempt = 0
    last_exc: Exception | None = None
    while attempt < retries:
        attempt += 1
        try:
            return agent(payload)
        except Exception as exc:  # noqa: PERF203 - allow broad exception for agent errors
            last_exc = exc
            print(f"⚠️  {agent.__name__} failed on attempt {attempt}/{retries}: {exc}")
            if attempt < retries:
                time.sleep(delay)

    if skip_on_fail:
        print(f"⏭️  Skipping {agent.__name__} after {retries} failed attempts")
        return {"status": "skipped", "error": str(last_exc) if last_exc else "unknown"}

    raise last_exc if last_exc else RuntimeError("Unknown agent error")
