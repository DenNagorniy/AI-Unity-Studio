from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict, List, Tuple

from agents.tech import feature_inspector, refactor_agent, tester
from agents.creative import lore_validator


Vote = Tuple[str, str]


def _vote_inspector(feature: str, out_dir: str) -> Tuple[str, str, str]:
    res = feature_inspector.run({"feature": feature, "out_dir": out_dir})
    verdict = res.get("verdict")
    if verdict == "Pass":
        return "FeatureInspectorAgent", "accept", ""
    return "FeatureInspectorAgent", "needs_revision", verdict or "issues found"


def _vote_lore(feature: str, out_dir: str) -> Tuple[str, str, str]:
    res = lore_validator.run({"feature": feature, "out_dir": out_dir, "description": "", "assets": [], "dialogues": ""})
    status = res.get("status")
    if status == "LorePass":
        return "LoreValidatorAgent", "accept", ""
    return "LoreValidatorAgent", "block", status or "lore mismatch"


def _vote_refactor() -> Tuple[str, str, str]:
    res = refactor_agent.run({})
    if not res.get("returncode") and not res.get("dead_code"):
        return "RefactorAgent", "accept", ""
    reason = "dead code" if res.get("dead_code") else "issues"
    return "RefactorAgent", "needs_revision", reason


def _vote_tests() -> Tuple[str, str, str]:
    res = tester.run({})
    failed = res.get("failed", 0)
    if failed:
        return "TesterAgent", "block", f"{failed} failed"
    return "TesterAgent", "accept", ""


def run(data: Dict | None = None) -> Dict:
    data = data or {}
    feature = data.get("feature", "unknown")
    out_dir = Path(data.get("out_dir", "ci_reports"))
    out_dir.mkdir(parents=True, exist_ok=True)

    votes: List[Tuple[str, str, str]] = [
        _vote_inspector(feature, str(out_dir)),
        _vote_lore(feature, str(out_dir)),
        _vote_refactor(),
        _vote_tests(),
    ]

    final = "accept"
    if any(v[1] == "block" for v in votes):
        final = "block"
    elif any(v[1] == "needs_revision" for v in votes):
        final = "needs_revision"

    lines = [
        "# AI Review Panel",
        "",
        "| Агент | Вердикт | Причина |",
        "|-------|---------|---------|",
    ]
    for agent, verdict, reason in votes:
        lines.append(f"| {agent} | {verdict} | {reason} |")
    lines.append("")
    lines.append(f"**Final Verdict:** {final}")
    lines.append("")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit = "unknown"
    lines.append(f"*Time:* {datetime.utcnow().isoformat()}")
    lines.append(f"*Feature:* {feature}")
    lines.append(f"*Commit:* {commit}")

    report_path = out_dir / "review_verdict.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {"verdict": final, "report": str(report_path)}


if __name__ == "__main__":
    print(run())
