from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from seven_gc_twin.integrations.campus_design import (
    SITE_IDS,
    adapt_campus_design_bundle,
    run_mlv_to_7gc_adapter,
)


def test_adapter_propagates_authored_planning_layout():
    design = {
        "site_id": "gary",
        "campus_slug": "gary",
        "phase": "FULL",
        "geometry_fidelity": "AUTHORED_PLANNING_LAYOUT",
        "source_manifest_sha256": "520cbba99541b1505ebba899a2f34bfa905eadd7af8f5b5e8fa050c884067be1",
        "zones": [
            {
                "campus_requirement_id": "GARY.FULL.HARDWARE_REPAIR_LAB",
                "material_assumption": "drywall_and_concrete_planning",
            }
        ],
        "service_intents": [{"template": "repair_lab"}],
        "candidate_infrastructure": [{"node_id": "gary-indoor-ap-1"}],
        "aggregate_demand": {"values": {"users_proxy": 24}},
        "evidence_class": "SIMULATED",
    }
    twin = adapt_campus_design_bundle(design)
    assert twin["site_id"] == "gary"
    assert twin["service_demand"]["values"]["geometry_fidelity"] == "AUTHORED_PLANNING_LAYOUT"
    assert "GARY.FULL.HARDWARE_REPAIR_LAB" in twin["service_demand"]["values"]["rooms_zones"]


def test_mlv_to_7gc_adapter_seven_campus():
    field_kit = Path(__file__).resolve().parents[2] / "field-kit"
    if not (field_kit / "control_plane" / "closed_loop.py").is_file():
        return
    report = run_mlv_to_7gc_adapter()
    assert report["MLV_TO_7GC_ADAPTER_PASS"] == "7/7"
    assert report["campuses"] == list(SITE_IDS)
