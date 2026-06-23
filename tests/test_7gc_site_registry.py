from pathlib import Path

import yaml

from site_buildings.export_bundle import export_all
from site_buildings.room_adjacency import build_adjacency
from site_buildings.site_registry import SITE_IDS
from site_buildings.svg_floorplan_export import export_svg

ROOT = Path(__file__).resolve().parents[1]


def test_site_registry():
    assert len(SITE_IDS) == 7


def test_room_adjacency_all_sites():
    for sid in SITE_IDS:
        adj = build_adjacency(sid)
        assert adj["site_id"] == sid
        assert len(adj["nodes"]) >= 4


def test_floorplan_svg_all_sites():
    for sid in SITE_IDS:
        svg = export_svg(sid)
        assert "<svg" in svg
        assert "Conceptual only" in svg


def test_building_configs_valid_yaml():
    for sid in SITE_IDS:
        for name in ["room_program.yaml", "rf_targets.yaml", "floorplan_blocks.yaml"]:
            path = ROOT / "configs" / "buildings" / sid / name
            assert path.exists(), f"missing {path}"
            data = yaml.safe_load(path.read_text())
            assert data["site_id"] == sid


def test_exports_generated():
    paths = export_all(ROOT / "results" / "exports")
    assert len(paths) == 7
    for sid, artifacts in paths.items():
        assert artifacts["svg"].exists()
        assert artifacts["materials"].exists()


def test_acoustic_rf_tradeoff_no_wall_leakage():
    from site_buildings.rf_scoring import rf_tradeoff

    r = rf_tradeoff("flexible_classroom")
    assert r["rely_on_wall_leakage"] is False
    assert r["ap_in_zone"] is True


def test_non_claim_policy_graham_land():
    from site_buildings.evidence_flags import evidence_flags

    flags = evidence_flags("graham_land")
    assert flags["flags"].get("no_antarctic_construction_claim") is True


def test_gaza_privacy_flags():
    from site_buildings.evidence_flags import evidence_flags

    flags = evidence_flags("gaza")
    assert flags["flags"].get("no_sensitive_location_publish") is True
