from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from pathlib import Path


PACKAGE_NAME = "Module_14_Capstone_Evidence_Gated_Medical_LLMs_Package_Ravi_Bajaj"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_manifest_bytes(raw: bytes) -> list[dict[str, str]]:
    text = raw.decode("utf-8", errors="strict")
    return list(csv.DictReader(io.StringIO(text)))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_package_directory_matches_manifest() -> None:
    package_dir = repo_root() / "outputs" / PACKAGE_NAME
    manifest_path = package_dir / "MANIFEST_SHA256.csv"
    rows = read_manifest_bytes(manifest_path.read_bytes())

    assert rows, "manifest must contain at least one packaged artifact"
    for row in rows:
        artifact = package_dir / row["path"]
        data = artifact.read_bytes()
        assert artifact.exists(), row["path"]
        assert len(data) == int(row["bytes"]), row["path"]
        assert sha256(data) == row["sha256"], row["path"]


def test_package_zip_matches_embedded_manifest() -> None:
    zip_path = repo_root() / "outputs" / f"{PACKAGE_NAME}.zip"
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path) as archive:
        manifest_names = [
            name for name in archive.namelist() if name.endswith("MANIFEST_SHA256.csv")
        ]
        assert manifest_names == [f"{PACKAGE_NAME}/MANIFEST_SHA256.csv"]
        rows = read_manifest_bytes(archive.read(manifest_names[0]))

        assert rows, "embedded manifest must contain at least one packaged artifact"
        for row in rows:
            name = f"{PACKAGE_NAME}/{row['path']}"
            data = archive.read(name)
            assert len(data) == int(row["bytes"]), name
            assert sha256(data) == row["sha256"], name
