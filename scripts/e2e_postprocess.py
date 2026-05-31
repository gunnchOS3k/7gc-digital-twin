#!/usr/bin/env python3
"""Copy CLI outputs into results/e2e/ for 7gc."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E2E = ROOT / "results" / "e2e"
E2E.mkdir(parents=True, exist_ok=True)

for src_name, dst_name in [("gary_summary.json", "gary_export.json"), ("gary_export.json", "gary_export.json")]:
    src = ROOT / "results" / src_name
    if src.exists():
        shutil.copy(src, E2E / dst_name)

summary = ROOT / "results" / "gary_summary.json"
if summary.exists():
    data = json.loads(summary.read_text())
    (E2E / "gary_summary.md").write_text(
        "# Gary E2E Summary\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in data.items()) + "\n"
    )
