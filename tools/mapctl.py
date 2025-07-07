import json
import pathlib
import sys
from pathlib import Path
from typing import Dict

import click
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
        click.echo("INFO: project_map.json not found – creating empty stub.")
        PM_PATH.write_text('{"schema_version":1,"features":{}}', encoding="utf-8")

    try:
        data = json.loads(PM_PATH.read_text(encoding="utf-8"))
        # Compatible validation for both pydantic v1 and v2
        if hasattr(ProjectMap, "model_validate"):
            ProjectMap.model_validate(data, strict=True)
        else:
            ProjectMap.parse_obj(data)
        click.secho("[OK] project_map.json is valid", fg="green")
        sys.exit(0)
    except (json.JSONDecodeError, ValidationError) as err:
        click.secho("[ERROR] project_map.json invalid", fg="red")
        click.echo(err)
        sys.exit(1)


@cli.command()
def summary():
    """Краткая сводка по фичам."""
    if not PM_PATH.exists():
        click.echo("project_map.json not found")
        return

    data = json.loads(PM_PATH.read_text(encoding="utf-8"))
    feats = data.get("features", {})
    tested_count = sum(1 for f in feats.values() if f.get("tested"))
    for name, feat in feats.items():
        tested = "[OK]" if feat.get("tested") else "[FAIL]"
        files = len(feat.get("files", []))
        click.echo(f"{name}: {tested} files={files}")
    total = len(feats)
    if total:
        coverage = tested_count / total * 100
        click.echo(f"\nCoverage: {coverage:.1f}% ({tested_count}/{total})")


@cli.command()
def index():
    """Generate FeatureIndex.md from project_map.json."""
    if not PM_PATH.exists():
        click.echo("project_map.json not found")
        return

    data = json.loads(PM_PATH.read_text(encoding="utf-8"))
    feats = data.get("features", {})
    lines = ["# Feature Index", "", "| Feature | Tested | Files |", "|---------|--------|-------|"]
    for name, feat in feats.items():
        tested = "✅" if feat.get("tested") else "❌"
        files = len(feat.get("files", []))
        lines.append(f"| {name} | {tested} | {files} |")

    Path("FeatureIndex.md").write_text("\n".join(lines), encoding="utf-8")
    click.secho("FeatureIndex.md updated", fg="green")


if __name__ == "__main__":
    cli()
