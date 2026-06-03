#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from seven_gc_twin.tool_adapters import sionna_export, aerial_dt_export, oran_policy_export, ns3_scenario_export
for mod in [sionna_export, aerial_dt_export, oran_policy_export, ns3_scenario_export]:
    print(mod.export("gary"))
