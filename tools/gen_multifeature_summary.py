from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
TEMPLATE_NAME = "multifeature_summary.html.j2"


def generate_multifeature_summary(
    reports_dir: str,
    results: List[Dict[str, Any]],
    total_time: float,
) -> Path:
    """Generate multifeature_summary.html in given directory."""
    metadata = {
        "date": datetime.utcnow().isoformat(),
        "total_time": round(total_time, 2),
        "count": len(results),
        "success": sum(1 for r in results if r.get("status") == "success"),
        "errors": sum(1 for r in results if r.get("status") == "error"),
    }
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(TEMPLATE_NAME)
    html = template.render(results=results, metadata=metadata)
    out_dir = Path(reports_dir)
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "multifeature_summary.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    import json
    import sys

    directory = sys.argv[1]
    data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    path = generate_multifeature_summary(directory, data, float(sys.argv[3]))
    print(path)
