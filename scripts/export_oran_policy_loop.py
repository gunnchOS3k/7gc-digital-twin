#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from seven_gc_twin.tool_adapters.oran_policy_export import export
p = argparse.ArgumentParser()
p.add_argument("--site", default="gary")
a = p.parse_args()
print(export(a.site))
