# tools/mapctl.py
import json, sys, pathlib, click
from typing import Dict
from pydantic import BaseModel, Field, ValidationError

# ---------- Pydantic schema ----------
class Feature(BaseModel):
    name: str
    files: list[str] = Field(default_factory=list)
    created_by: str | None = None
    tested: bool | None = False

class ProjectMap(BaseModel):
    schema_version: int = 1
    features: Dict[str, Feature] = Field(default_factory=dict)
# -------------------------------------

PM_PATH = pathlib.Path("project_map.json")

@click.group()
def cli():
    """mapctl – проверка project_map.json"""
    pass

@cli.command()
def validate():
    """Строгая валидация project_map.json"""
    if not PM_PATH.exists():
        click.echo("ℹ️  project_map.json not found – creating empty stub.")
        PM_PATH.write_text('{"schema_version":1,"features":{}}', encoding="utf-8")

    try:
        data = json.loads(PM_PATH.read_text(encoding="utf-8"))
        ProjectMap.model_validate(data,
                                  strict=True)  # pydantic v2
        click.secho("✅ project_map.json is valid", fg="green")
        sys.exit(0)
    except (json.JSONDecodeError, ValidationError) as err:
        click.secho("❌ project_map.json invalid", fg="red")
        click.echo(err)
        sys.exit(1)

if __name__ == "__main__":
    cli()
