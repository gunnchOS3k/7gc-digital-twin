from site_buildings.floorplan_model import build_floorplan_blocks
from site_buildings.site_registry import SITE_IDS


def test_floorplan_footprints():
    for sid in SITE_IDS:
        for fp in ["minimum_pilot", "semi_permanent_hub", "full_campus"]:
            model = build_floorplan_blocks(sid, fp)
            assert model["footprint"] == fp
            assert len(model["blocks"]) >= 4
