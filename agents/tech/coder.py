from __future__ import annotations
from pathlib import Path
import config

def coder(task_spec):
    """Generate a simple C# helper file patch."""
    path = task_spec.get("path", "Generated/Helper.cs")
    namespace = task_spec.get("namespace", "AIUnityStudio.Generated")

    class_name = Path(path).stem
    code = (
        f"namespace {namespace} {{\n"
        f"    public static class {class_name} {{\n"
        f"        public static int Square(int x) => x * x;\n"
        f"    }}\n"
        f"}}\n"
    )

    return {
        "modifications": [
            {
                "path": path,
                "content": code,
                "action": "overwrite",
            }
        ]
    }

def run(task_spec):
    """Public wrapper used by the orchestrator."""
    return coder(task_spec)
