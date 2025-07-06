def run(input: dict) -> dict:
    """ArchitectAgent stub: selects path/namespace and returns updated task."""
    feature = input.get("feature") or input.get("task") or input.get("tasks", [{}])[0].get("feature")
    if isinstance(feature, dict):
        feature = feature.get("feature")
    path = "Assets/Scripts/Features/" + str(feature).replace(" ", "") + ".cs"
    namespace = "MyProject.Features"
    asmdef = "MyProject.Features.asmdef"
    return {
        "feature": feature,
        "task": input.get("task"),
        "path": path,
        "namespace": namespace,
        "asmdef": asmdef,
    }
