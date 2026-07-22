"""Shared Gate 2 helpers for 7GC."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def resolve_schema_dir(schema_dir: str | Path | None = None) -> Path:
    if schema_dir is not None:
        return Path(schema_dir).expanduser().resolve()
    env = os.environ.get("GATE2_CONTRACTS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    sibling = (
        Path(__file__).resolve().parents[3]
        / "gunnchos-7gc-ai-ran-field-kit"
        / "contracts"
    )
    if sibling.is_dir():
        return sibling
    raise FileNotFoundError("Pass --schema-dir or set GATE2_CONTRACTS_DIR")


def load_validator(schema_dir: Path):
    candidate = schema_dir.parent / "scripts" / "validate_contract.py"
    spec = importlib.util.spec_from_file_location("gate2_validate_contract", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {candidate}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def git_commit(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[3]
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return path
