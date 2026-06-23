"""Generate 7GC campus digital twin configs, docs, and exports."""
from __future__ import annotations

from pathlib import Path

import yaml

from site_buildings.export_bundle import export_all
from site_buildings.site_registry import SITE_IDS, get_site

ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_building_configs(site_id: str) -> None:
    site = get_site(site_id)
    base = ROOT / "configs" / "buildings" / site_id
    rooms = site["rooms"]
    configs = {
        "room_program.yaml": {
            "site_id": site_id,
            "display_name": site["display_name"],
            "rooms": [{"id": r, "acoustic_target": "moderate", "ap_in_zone": True} for r in rooms],
            "evidence_status": "design assumption",
            "label": "Conceptual only — not for construction",
        },
        "building_concept.yaml": {
            "site_id": site_id,
            "footprints": ["minimum_pilot", "semi_permanent_hub", "full_campus"],
            "evidence_status": "design assumption",
        },
        "material_options.yaml": {"site_id": site_id, "expert_review_needed": True},
        "acoustic_targets.yaml": {
            "site_id": site_id,
            "strategy": "sound-isolated partitions between learning zones",
            "not_fully_soundproof": True,
        },
        "rf_targets.yaml": {
            "site_id": site_id,
            "ap_per_zone": True,
            "wired_backbone": True,
            "no_wall_leakage_model": True,
        },
        "power_connectivity_assumptions.yaml": {
            "site_id": site_id,
            "edge_cache": True,
            "offline_server_where_needed": site_id in ("gaza", "ghana", "graham_land"),
        },
        "climate_assumptions.yaml": {"site_id": site_id, "units": "SI"},
        "risk_register.yaml": {
            "site_id": site_id,
            "risks": [{"id": "overclaim", "mitigation": "non-claim policy"}],
        },
        "floorplan_blocks.yaml": {"site_id": site_id, "footprint_default": "semi_permanent_hub"},
    }
    for name, data in configs.items():
        _write(base / name, yaml.dump(data, sort_keys=False))


def generate_site_docs(site_id: str) -> None:
    site = get_site(site_id)
    base = ROOT / "docs" / "sites" / site_id
    banner = "> Conceptual only — not for construction\n\n"
    if site.get("privacy_sensitive"):
        banner += "> Do not publish sensitive locations.\n\n"
    if site.get("conceptual_only"):
        banner += "> No Antarctic construction claim.\n\n"

    docs = {
        "README.md": f"# {site['display_name']} Digital Twin\n\n{banner}",
        "_DIGITAL_TWIN_SPEC.md": f"# Digital Twin Spec\n\n{banner}Site ID: `{site_id}`\n",
        "_BUILDING_DIGITAL_TWIN_SPEC.md": "# Building Digital Twin Spec\n\nBlock floor plans only.\n",
        "_FLOOR_PLAN_CONCEPT.md": "# Floor Plan Concept\n\nSVG exports in results/exports/\n",
        "_ROOM_ADJACENCY_MODEL.md": "# Room Adjacency Model\n\nJSON graph exports.\n",
        "_SIGNAL_AND_ACOUSTIC_MODEL.md": "# Signal and Acoustic Model\n\nAP per zone; sound-isolated partitions.\n",
        "_MATERIAL_STRATEGY.md": "# Material Strategy\n\nCSV matrix exports.\n",
        "_DATA_DICTIONARY.md": "# Data Dictionary\n\n| Field | Type | Units |\n|-------|------|-------|\n| suitability_score | float | 0-1 |\n",
        "_VALIDATION_PLAN.md": "# Validation Plan\n\nExpert review required before construction.\n",
    }
    for name, body in docs.items():
        _write(base / name, body)


def generate_canon_docs() -> None:
    base = ROOT / "docs" / "sites"
    _write(
        base / "README.md",
        "# 7GC Digital Twin Sites\n\nSeven WAIKE UPNOW campus digital twins.\n",
    )
    canon = [
        "7GC_DIGITAL_TWIN_SITE_CANON.md",
        "7GC_BUILDING_DIGITAL_TWIN_SPEC.md",
        "7GC_ROOM_ADJACENCY_CANON.md",
        "7GC_SIGNAL_AND_ACOUSTIC_MODEL.md",
        "7GC_MATERIAL_SCORING_MODEL.md",
        "7GC_FLOOR_PLAN_GENERATION_SPEC.md",
        "7GC_EXPORTS_AND_VALIDATION.md",
    ]
    for name in canon:
        _write(base / name, f"# {name.replace('.md','').replace('_',' ')}\n\nConceptual only — not for construction.\n")


def generate_cross_repo() -> None:
    base = ROOT / "docs" / "7gc"
    for name in [
        "CROSS_REPO_HANDOFF.md",
        "7GC_MASTER_INDEX.md",
        "7GC_REPO_MAP.md",
        "7GC_EVIDENCE_MATRIX.md",
        "7GC_NON_CLAIM_POLICY.md",
        "7GC_SITE_COMPLETION_MATRIX.md",
    ]:
        _write(base / name, f"# {name}\n\nSee waike-research-ops for curriculum handoff.\n")
    for sid in SITE_IDS:
        _write(
            base / "sites" / sid / "CROSS_REPO_HANDOFF.md",
            f"# Cross-repo handoff — {sid}\n",
        )


def generate_all() -> None:
    generate_canon_docs()
    generate_cross_repo()
    for sid in SITE_IDS:
        generate_building_configs(sid)
        generate_site_docs(sid)
    export_all(ROOT / "results" / "exports")
    print(f"Generated digital twin bundle for {len(SITE_IDS)} sites")


if __name__ == "__main__":
    generate_all()
