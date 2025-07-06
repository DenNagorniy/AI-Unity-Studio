import os
import subprocess
import tempfile
import json

def coder(task_spec):
    code = (
        "public static class MathHelper\n"
        "{\n"
        "    public static int Square(int x)\n"
        "    {\n"
        "        return x * x;\n"
        "    }\n"
        "}"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        csproj_path = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.csproj")
        code_path = os.path.join(temp_dir, "MathHelper.cs")

        # Создаём проект
        subprocess.run(["dotnet", "new", "classlib", "--output", temp_dir], check=True)

        # Сохраняем код
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Компилируем проект
        result = subprocess.run(
            ["dotnet", "build", csproj_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise ValueError("dotnet build failed")

        print("🎉 Компиляция успешна!")

    # Возвращаем модификацию с правильным action
    return {
        "modifications": [
            {
                "path": "MathHelper.cs",
                "content": code,
                "action": "overwrite"
            }
        ]
    }
