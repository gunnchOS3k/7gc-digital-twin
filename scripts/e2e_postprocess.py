#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E2E = ROOT / "results" / "e2e"
E2E.mkdir(parents=True, exist_ok=True)
env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}

subprocess.run([sys.executable, "-m", "seven_gc_twin.cli", "metrics", "gary", "--toy"], cwd=ROOT, env=env, check=True)
subprocess.run([sys.executable, "-m", "seven_gc_twin.cli", "make-report", "gary"], cwd=ROOT, env=env, check=True)

for name in ("gary_summary.json", "gary_export.json"):
    src = ROOT / "results" / name
    if src.exists():
        shutil.copy(src, E2E / name.replace("gary_summary.json", "gary_export.json") if "summary" in name else E2E / name)

summary = ROOT / "results" / "gary_summary.json"
if summary.exists():
    data = json.loads(summary.read_text())
    (E2E / "gary_summary.md").write_text("# Gary E2E Summary\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in data.items()) + "\n")

toy = E2E / "gary_toy_metrics.json"
if not toy.exists():
    alt = ROOT / "results" / "e2e" / "gary_toy_metrics.json"
    if alt.exists():
        shutil.copy(alt, toy)
