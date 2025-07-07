from __future__ import annotations

"""SelfMonitorAgent analyzes pipeline stability and efficiency."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "self_monitor_report.md.j2"


class SelfMonitorAgent:
    """Analyze logs and produce self-monitor_report.md."""

    def __init__(
        self,
        out_dir: str = "ci_reports",
        journal_path: Path | None = None,
        trace_path: Path | None = None,
        memory_path: Path | None = None,
    ) -> None:
        self.out_dir = Path(out_dir)
        self.journal_path = journal_path or Path("agent_journal.log")
        self.trace_path = trace_path or Path("agent_trace.log")
        self.memory_path = memory_path or Path("agent_memory.json")

    # parsing helpers
    def _parse_journal(self) -> tuple[Dict[str, int], Dict[str, int], Dict[str, Dict[str, int]]]:
        counts: Dict[str, int] = {}
        reruns: Dict[str, int] = {}
        fails_after: Dict[str, Dict[str, int]] = {}
        if not self.journal_path.exists():
            return counts, reruns, fails_after
        prev_agent = None
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            if "| AUTO_FIX |" in line:
                continue
            if "[" not in line or "]" not in line:
                continue
            agent = line.split("[", 1)[1].split("]", 1)[0]
            counts[agent] = counts.get(agent, 0) + 1
            if prev_agent == agent:
                reruns[agent] = reruns.get(agent, 0) + 1
            if "error" in line.lower():
                if prev_agent:
                    fails_after.setdefault(agent, {})[prev_agent] = fails_after.get(agent, {}).get(prev_agent, 0) + 1
            prev_agent = agent
        return counts, reruns, fails_after

    def _parse_memory(self) -> tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
        success: Dict[str, int] = {}
        fail: Dict[str, int] = {}
        autofix: Dict[str, int] = {}
        if not self.memory_path.exists():
            return success, fail, autofix
        try:
            data = json.loads(self.memory_path.read_text(encoding="utf-8"))
            log = data.get("learning_log", {})
        except Exception:
            return success, fail, autofix
        for agent, entries in log.items():
            if agent.startswith("AutoFix:"):
                base = agent.split("AutoFix:", 1)[1]
                autofix[base] = len(entries)
                continue
            succ = sum(1 for e in entries if e.get("result") == "success")
            success[agent] = succ
            fail[agent] = len(entries) - succ
        return success, fail, autofix

    def _parse_trace(self) -> Dict[str, float]:
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
        return {a: round(durations[a] / counts[a], 2) for a in durations}

    def _build_rows(self) -> List[Dict[str, Any]]:
        counts, reruns, fails_after = self._parse_journal()
        success, fail, autofix = self._parse_memory()
        avg_time = self._parse_trace()
        agents = set(counts) | set(success) | set(fail) | set(autofix) | set(avg_time)
        rows: List[Dict[str, Any]] = []
        for ag in sorted(agents):
            calls = counts.get(ag, 0)
            s_cnt = success.get(ag, 0)
            f_cnt = fail.get(ag, 0)
            total = s_cnt + f_cnt if (s_cnt + f_cnt) else calls
            rate = s_cnt / total if total else 0.0
            rerun_freq = reruns.get(ag, 0) / calls if calls else 0.0
            auto_freq = autofix.get(ag, 0) / calls if calls else 0.0
            problems: List[str] = []
            if rate < 0.8:
                problems.append("низкая успешность")
            if rerun_freq > 0.1:
                problems.append("частые перезапуски")
            after = fails_after.get(ag)
            if after:
                prev = max(after.items(), key=lambda x: x[1])[0]
                problems.append(f"падает после {prev}")
            rows.append(
                {
                    "agent": ag,
                    "success": round(rate * 100, 1),
                    "avg_time": avg_time.get(ag),
                    "autofix": round(auto_freq * 100, 1) if calls else 0.0,
                    "problems": ", ".join(problems) or "",
                }
            )
        return rows

    def _render(self, rows: List[Dict[str, Any]]) -> str:
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        template = env.get_template(TEMPLATE_NAME)
        return template.render(rows=rows, generated=datetime.utcnow().isoformat())

    def run(self) -> Dict[str, Any]:
        rows = self._build_rows()
        text = self._render(rows)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.out_dir / "self_monitor_report.md"
        out_path.write_text(text, encoding="utf-8")
        return {"status": "success", "report": str(out_path)}


if __name__ == "__main__":
    print(SelfMonitorAgent().run())
