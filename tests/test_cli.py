import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_summarize_gary():
    r = subprocess.run(
        [sys.executable, "-m", "seven_gc_twin.cli", "summarize", "gary"],
        cwd=ROOT,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "gary" in r.stdout
