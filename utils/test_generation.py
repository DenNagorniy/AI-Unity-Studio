import re
from pathlib import Path
import json


def is_static_class(script_path: str, source_code: str | None = None) -> bool:
    """Return True if the C# class defined in script_path or code is static."""
    path = Path(script_path)
    class_name = path.stem
    if source_code:
        text = source_code
    else:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return False
    pattern = rf"static\s+class\s+{re.escape(class_name)}\b"
    return re.search(pattern, text) is not None


def generate_test_files(
    script_path: str, namespace: str, source_code: str | None = None
) -> list[dict]:
    """Return patch modifications for basic tests of the given C# script."""
    class_name = Path(script_path).stem
    is_static = is_static_class(script_path, source_code)
    test_ns = f"{namespace}.Tests"
    test_dir = Path("Assets/Tests/Generated")
    logic_path = test_dir / f"Test_{class_name}_Logic.cs"
    behaviour_path = test_dir / f"Test_{class_name}_Behaviour.cs"

    if is_static:
        logic_content = (
            "// Auto-generated test\n"
            f"using NUnit.Framework;\n"
            f"using {namespace};\n\n"
            f"namespace {test_ns}\n"
            "{\n"
            f"    public class Test_{class_name}_Logic\n"
            "    {\n"
            "        [Test]\n"
            "        public void StaticClassIsAccessible()\n"
            "        {\n"
            f"            Assert.IsNotNull(typeof({class_name}));\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
        behaviour_content = (
            "// Auto-generated test\n"
            "using UnityEngine.TestTools;\n"
            "using NUnit.Framework;\n"
            "using System.Collections;\n\n"
            f"namespace {test_ns}\n"
            "{\n"
            f"    public class Test_{class_name}_Behaviour\n"
            "    {\n"
            "        [UnityTest]\n"
            "        public IEnumerator DummyBehaviourTest()\n"
            "        {\n"
            "            yield return null;\n"
            "            Assert.Pass();\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
    else:
        logic_content = (
            "// Auto-generated test\n"
            f"using NUnit.Framework;\n"
            f"using {namespace};\n\n"
            f"namespace {test_ns}\n"
            "{\n"
            f"    public class Test_{class_name}_Logic\n"
            "    {\n"
            "        [Test]\n"
            f"        public void {class_name}_CanBeInstantiated()\n"
            "        {\n"
            f"            var instance = new {class_name}();\n"
            "            Assert.IsNotNull(instance);\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
        behaviour_content = (
            "// Auto-generated test\n"
            "using UnityEngine.TestTools;\n"
            "using NUnit.Framework;\n"
            "using UnityEngine;\n"
            "using System.Collections;\n\n"
            f"namespace {test_ns}\n"
            "{\n"
            f"    public class Test_{class_name}_Behaviour\n"
            "    {\n"
            "        [UnityTest]\n"
            f"        public IEnumerator {class_name}ExistsInScene()\n"
            "        {\n"
            f"            var go = GameObject.FindObjectOfType<{class_name}>();\n"
            f"            Assert.IsNotNull(go, \"{class_name} script is not found in the scene.\");\n"
            "            yield return null;\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

    return [
        {"path": str(logic_path), "content": logic_content, "action": "overwrite"},
        {
            "path": str(behaviour_path),
            "content": behaviour_content,
            "action": "overwrite",
        },
    ] + ensure_asmdef_patch()


def ensure_asmdef_patch() -> list[dict]:
    """Return patch for GeneratedTests.asmdef if it doesn't exist."""
    asmdef_path = Path("Assets/Tests/Generated/GeneratedTests.asmdef")
    if asmdef_path.exists():
        return []

    asmdef_content = json.dumps(
        {
            "name": "GeneratedTests",
            "references": ["AIUnityStudio.Generated", "UnityEngine.TestRunner"],
            "includePlatforms": [],
            "excludePlatforms": [],
            "allowUnsafeCode": False,
            "overrideReferences": False,
            "precompiledReferences": [],
            "autoReferenced": True,
            "defineConstraints": [],
            "versionDefines": [],
            "noEngineReferences": False,
            "optionalUnityReferences": [],
            "testAssemblies": True,
        },
        indent=2,
    )

    return [{"path": str(asmdef_path), "content": asmdef_content, "action": "overwrite"}]
