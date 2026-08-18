#!/usr/bin/env python3
"""Independent digital reproduction of the RQ1 synthetic path."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _pytest_cmd() -> list[str]:
    return [sys.executable, "-m", "pytest", "-q"]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(SRC)}
    start = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    steps = [
        [*_pytest_cmd(), "tests/test_rq1_supervisor_digital.py", "tests/test_site_profiles_operational.py"],
        [sys.executable, "-m", "seven_gc_twin.cli", "validate-site", "gary"],
        [sys.executable, "-m", "seven_gc_twin.cli", "build-scene", "gary", "--mode", "synthetic-fixture"],
        [sys.executable, "-m", "seven_gc_twin.cli", "run-experiment", "rq1_gary_flagship_profiles"],
    ]
    for cmd in steps:
        r = subprocess.run(cmd, cwd=ROOT, env=env)
        if r.returncode != 0:
            return r.returncode
    artifact = ROOT / "results/experiments/rq1_gary_flagship_profiles.json"
    if not artifact.exists():
        print("missing experiment artifact", file=sys.stderr)
        return 1
    record = {
        "repo": "7gc-digital-twin",
        "research_question": "RQ1",
        "command": "make reproduce",
        "start": start,
        "end": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "result": "PASS",
        "artifact": str(artifact.relative_to(ROOT)),
        "output_hashes": {str(artifact.relative_to(ROOT)): _sha256(artifact)},
        "evidence_status": "synthetic_fixture",
        "non_claims": [
            "Not independent human sign-off",
            "Not RF campaign measurement",
            "Not community deployment",
            "Not University of Oulu affiliation",
        ],
    }
    out = ROOT / "results/reproduce/REPRODUCE_RECORD.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "sha256": record["output_hashes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
