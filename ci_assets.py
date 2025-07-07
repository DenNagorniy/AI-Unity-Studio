"""Generate assets based on descriptions and update catalog."""

from __future__ import annotations

import json
import os
from pathlib import Path

from utils.asset_catalog import catalog_assets
from utils.asset_generator import generate_from_specs
from utils.asset_qc import run_qc
from tools.gen_assets_report import generate_assets_report


REQUESTS_FILE = Path(os.getenv("ASSET_REQUESTS", "asset_requests.json"))


def _load_specs() -> list[dict[str, str]]:
    if REQUESTS_FILE.exists():
        with REQUESTS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def main() -> None:
    specs = _load_specs()
    generated = generate_from_specs(specs)
    run_qc()
    catalog_assets()

    reports = Path(os.getenv("CI_REPORTS_DIR", "ci_reports"))
    reports.mkdir(exist_ok=True)
    generate_assets_report(out_dir=str(reports))
    out_path = reports / "ci_assets.json"
    out_text = json.dumps(generated, indent=2, ensure_ascii=False)
    out_path.write_text(out_text, encoding="utf-8")
    print(json.dumps(generated, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
