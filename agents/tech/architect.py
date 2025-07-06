def run(input: dict) -> dict:
    """
    Выбирает путь, namespace, asmdef и возвращает обновлённую задачу.
    """
    feature = input.get("feature")
    path = "Assets/Scripts/Features/" + feature.replace(" ", "") + ".cs"
    namespace = "MyProject.Features"
    asmdef = "MyProject.Features.asmdef"
    return {
        "feature": feature,
        "task": input.get("task"),
        "path": path,
        "namespace": namespace,
        "asmdef": asmdef
    }