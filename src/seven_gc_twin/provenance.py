"""Provenance stamps for synthetic RQ1 artifacts.

Never labels synthetic outputs as field-validated RF or community-deployment evidence.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[2]
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except Exception:
        return "unknown"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_json(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(blob)


def stamp(
    *,
    artifact_kind: str,
    site_id: str,
    mode: str,
    extra: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    evidence = "synthetic_fixture" if mode in {"smoke", "synthetic-fixture", "toy"} else mode
    payload = {
        "schema_name": "gunnchos.twin_provenance",
        "schema_version": "1.0.0",
        "artifact_kind": artifact_kind,
        "site_id": site_id,
        "mode": mode,
        "evidence_status": evidence,
        "producer": {
            "repository": "7gc-digital-twin",
            "commit": git_commit(repo_root),
            "generated_at": utc_now_iso(),
        },
        "non_claims": [
            "Not a community deployment",
            "Not an RF campaign measurement",
            "Not University of Oulu affiliation",
            "Not field-validated unless evidence_status says otherwise",
        ],
    }
    if extra:
        payload["extra"] = extra
    payload["content_sha256"] = sha256_json({k: v for k, v in payload.items() if k != "content_sha256"})
    return payload
