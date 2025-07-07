"""Upload build artifacts to an S3 compatible storage."""

from __future__ import annotations

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv


def _load_env() -> dict[str, str]:
    load_dotenv()
    required = [
        "S3_ENDPOINT",
        "S3_ACCESS_KEY",
        "S3_SECRET_KEY",
        "S3_BUCKET",
    ]
    config = {var: os.getenv(var) for var in required}
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise RuntimeError(f"Missing env variables: {', '.join(missing)}")
    return config


def _get_client(cfg: dict[str, str]):
    return boto3.client(
        "s3",
        endpoint_url=cfg["S3_ENDPOINT"],
        aws_access_key_id=cfg["S3_ACCESS_KEY"],
        aws_secret_access_key=cfg["S3_SECRET_KEY"],
    )


def _upload_file(client, bucket: str, path: Path) -> None:
    key = path.name
    client.upload_file(str(path), bucket, key)
    print(f"Uploaded {path} -> {bucket}/{key}")


def main() -> None:
    cfg = _load_env()
    client = _get_client(cfg)
    bucket = cfg["S3_BUCKET"]

    artifacts = []
    reports_dir = Path("ci_reports")
    if reports_dir.exists():
        artifacts.extend(p for p in reports_dir.iterdir() if p.suffix in {".zip", ".apk"})

    for path in artifacts:
        _upload_file(client, bucket, path)


if __name__ == "__main__":
    main()
