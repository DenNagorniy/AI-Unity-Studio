from __future__ import annotations

"""MetaAgent analyzes CI data and produces optimization insights."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "meta_insights.md.j2"


class MetaAgent:
    """Analyze pipeline data and generate meta_insights.md."""

    def __init__(
        self,
        out_dir: str = "ci_reports",
        memory_path: Path | None = None,
        journal_path: Path | None = None,
        trace_path: Path | None = None,
        feedback_path: Path | None = None,
    ) -> None:
        self.out_dir = Path(out_dir)
        self.memory_path = memory_path or Path("agent_memory.json")
        self.journal_path = journal_path or Path("agent_journal.log")
        # prefer jsonl/log if exists, else html
        self.trace_path = trace_path or Path("trace_report.jsonl")
        if not self.trace_path.exists():
            self.trace_path = Path("agent_trace.log")
        self.feedback_path = feedback_path or Path("user_feedback_report.md")

    # internal helpers
    def _load_memory(self) -> Dict[str, List[dict]]:
        if not self.memory_path.exists():
            return {}
        try:
            data = json.loads(self.memory_path.read_text(encoding="utf-8"))
            return data.get("learning_log", {})
        except Exception:
            return {}

    def _parse_journal(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        if not self.journal_path.exists():
            return counts
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            if "[" in line and "]" in line:
                agent = line.split("[", 1)[1].split("]", 1)[0]
                counts[agent] = counts.get(agent, 0) + 1
        return counts

    def _parse_trace(self) -> Dict[str, Any]:
        durations: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        if not self.trace_path.exists():
            return {}
        for line in self.trace_path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
            except Exception:
                continue
            agent = item.get("agent")
            start = item.get("start_time")
            end = item.get("end_time")
            if not agent or not start or not end:
                continue
            try:
                s_dt = datetime.fromisoformat(start)
                e_dt = datetime.fromisoformat(end)
            except Exception:
                continue
            dur = (e_dt - s_dt).total_seconds()
            durations[agent] = durations.get(agent, 0.0) + dur
            counts[agent] = counts.get(agent, 0) + 1
        result = {
            a: {
                "avg_time": round(durations[a] / counts[a], 2),
                "calls": counts[a],
            }
            for a in durations
        }
        return result

    def _parse_feedback(self) -> Dict[str, float]:
        ratings: List[int] = []
        if not self.feedback_path.exists():
            return {"avg_rating": 0.0}
        for line in self.feedback_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and "|" in line[1:]:
                parts = [p.strip() for p in line.strip().split("|") if p.strip()]
                if len(parts) >= 2 and parts[0] != "Variant":
                    try:
                        ratings.append(int(parts[1]))
                    except ValueError:
                        continue
        avg = sum(ratings) / len(ratings) if ratings else 0.0
        return {"avg_rating": round(avg, 2)}

    def _build_context(self) -> Dict[str, Any]:
        log = self._load_memory()
        journal = self._parse_journal()
        trace = self._parse_trace()
        feedback = self._parse_feedback()

        failures: List[Dict[str, Any]] = []
        autofix: List[Dict[str, Any]] = []

        for agent, entries in log.items():
            if agent.startswith("AutoFix:"):
                base = agent.split("AutoFix:", 1)[1]
                patterns: Dict[str, int] = {}
                for e in entries:
                    out = e.get("output")
                    if out:
                        patterns[out] = patterns.get(out, 0) + 1
                repeated = sum(1 for c in patterns.values() if c > 1)
                if repeated:
                    autofix.append({"agent": base, "count": repeated})
            else:
                total = len(entries)
                fail = sum(1 for e in entries if e.get("result") != "success")
                if fail:
                    failures.append(
                        {
                            "agent": agent,
                            "fails": fail,
                            "total": total,
                            "rate": fail / total if total else 0.0,
                        }
                    )

        failures.sort(key=lambda x: x["rate"], reverse=True)

        performance = [
            {
                "agent": a,
                "avg_time": trace[a]["avg_time"],
                "calls": trace[a]["calls"],
            }
            for a in sorted(trace)
        ]

        return {
            "failures": failures,
            "autofix": autofix,
            "performance": performance,
            "quality": feedback,
        }

    def _render(self, context: Dict[str, Any]) -> str:
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        template = env.get_template(TEMPLATE_NAME)
        return template.render(**context)

    def run(self) -> Dict[str, Any]:
        """Generate meta insights markdown and return result info."""
        context = self._build_context()
        text = self._render(context)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.out_dir / "meta_insights.md"
        out_path.write_text(text, encoding="utf-8")
        return {"status": "success", "report": str(out_path)}


if __name__ == "__main__":
    print(MetaAgent().run())
