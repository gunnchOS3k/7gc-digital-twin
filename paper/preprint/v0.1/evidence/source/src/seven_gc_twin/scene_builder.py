"""Full 7GC digital twin scene pipeline — synthetic-fixture and open-data modes."""
from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .config.loader import load_site_config
from .site_profiles import load_profile

SITES = ["gary", "ghana", "guyana", "gaza", "geelong", "graham_land", "germany"]

CAMPUS_GEO = {
    "gary": {"country": "USA", "center": [-87.3464, 41.5934], "role": "flagship_urban"},
    "ghana": {"country": "Ghana", "center": [-0.187, 5.6037], "role": "mobile_first"},
    "guyana": {"country": "Guyana", "center": [-58.155, 6.801], "role": "hinterland"},
    "gaza": {"country": "Gaza", "center": [34.467, 31.502], "role": "remote_first"},
    "geelong": {"country": "Australia", "center": [144.361, -38.150], "role": "smart_city"},
    "graham_land": {"country": "Antarctica", "center": [-60.0, -64.0], "role": "polar"},
    "germany": {"country": "Germany", "center": [13.405, 52.520], "role": "privacy_equity"},
}


def scene_root(site_id: str) -> Path:
    return Path("results/scenes") / site_id


def _evidence(mode: str) -> str:
    if mode == "open-data":
        return "open_data_backed"
    if mode == "synthetic-fixture":
        return "smoke_test_only"
    return "calibrated_simulation"


def _fc(features: list) -> dict:
    return {"type": "FeatureCollection", "features": features}


def _point(lon: float, lat: float, props: dict) -> dict:
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def _poly_bbox(center: list[float], delta: float = 0.02) -> dict:
    lon, lat = center
    ring = [
        [lon - delta, lat - delta],
        [lon + delta, lat - delta],
        [lon + delta, lat + delta],
        [lon - delta, lat + delta],
        [lon - delta, lat - delta],
    ]
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]}, "properties": {}}


def build_geospatial(site_id: str, mode: str) -> dict[str, Path]:
    cfg = load_site_config(site_id)
    geo = CAMPUS_GEO[site_id]
    center = geo["center"]
    out = scene_root(site_id) / "geo"
    out.mkdir(parents=True, exist_ok=True)
    ev = _evidence(mode)
    anchors = [
        _point(center[0] - 0.005, center[1] + 0.003, {"type": "school_or_learning", "synthetic": True}),
        _point(center[0] + 0.004, center[1], {"type": "library_community", "synthetic": True}),
        _point(center[0], center[1] - 0.004, {"type": "small_business", "synthetic": True}),
    ]
    paths = {}
    for name, feats in [
        ("base_layers", [_poly_bbox(center)]),
        ("buildings", [_poly_bbox(center, 0.008)]),
        ("roads", [_point(center[0], center[1], {"road": "main_stub"})]),
        ("community_anchors", anchors),
        ("scene_bounds", [_poly_bbox(center, 0.03)]),
    ]:
        data = _fc(feats)
        data["properties"] = {"site_id": site_id, "evidence_status": ev, "data_mode": mode}
        p = out / f"{name}.geojson"
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        paths[name] = p
    return paths


def build_3d(site_id: str, mode: str) -> dict[str, Path]:
    out = scene_root(site_id) / "3d"
    out.mkdir(parents=True, exist_ok=True)
    ev = _evidence(mode)
    manifest = {
        "site_id": site_id,
        "scene_version": "1.0.0",
        "evidence_status": ev,
        "generator": "seven_gc_twin.scene_builder",
        "objects": ["ground_plane", "learning_anchor", "connectivity_volume"],
    }
    paths = {}
    paths["manifest"] = out / "scene_manifest.json"
    paths["manifest"].write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Minimal glTF 2.0
    gltf = {
        "asset": {"version": "2.0", "generator": "7gc-digital-twin"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3",
             "max": [1, 1, 0], "min": [-1, -1, 0]},
            {"bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteLength": 36},
            {"buffer": 0, "byteOffset": 36, "byteLength": 6},
        ],
        "buffers": [{"byteLength": 44}],
    }
    paths["gltf"] = out / "scene.gltf"
    paths["gltf"].write_text(json.dumps(gltf, indent=2) + "\n", encoding="utf-8")
    paths["summary"] = out / "scene_summary.md"
    paths["summary"].write_text(
        f"# 3D scene — {site_id}\n\nLow-fidelity procedural scene. Evidence: **{ev}**.\n", encoding="utf-8"
    )
    paths["materials"] = out / "materials.json"
    paths["materials"].write_text(json.dumps({"materials": [{"name": "default", "color": "#4a9eff"}]}, indent=2) + "\n", encoding="utf-8")
    paths["index"] = out / "object_index.json"
    paths["index"].write_text(json.dumps({"objects": manifest["objects"]}, indent=2) + "\n", encoding="utf-8")
    # Sionna prep XML
    root = ET.Element("scene", attrib={"site_id": site_id, "evidence_status": ev})
    ET.SubElement(root, "note").text = "Preparation artifact — install Sionna for RT validation"
    paths["sionna"] = out / "sionna_scene.xml"
    ET.ElementTree(root).write(paths["sionna"], encoding="utf-8", xml_declaration=True)
    paths["cesium"] = out / "cesium_config.json"
    lon, lat = CAMPUS_GEO[site_id]["center"]
    paths["cesium"].write_text(json.dumps({"longitude": lon, "latitude": lat, "height": 500}, indent=2) + "\n", encoding="utf-8")
    return paths


def build_connectivity(site_id: str, mode: str) -> dict[str, Path]:
    import yaml

    out = scene_root(site_id) / "connectivity"
    out.mkdir(parents=True, exist_ok=True)
    ev = _evidence(mode)
    center = CAMPUS_GEO[site_id]["center"]
    graph = {
        "site_id": site_id,
        "nodes": [
            {"id": "ap_school", "type": "wifi_zone"},
            {"id": "bs_stub", "type": "private_5g_zone"},
            {"id": "ntn_fallback", "type": "ntn_fallback_zone"},
        ],
        "edges": [{"from": "ap_school", "to": "bs_stub", "latency_ms_stub": 12}],
        "evidence_status": ev,
    }
    paths = {}
    paths["graph"] = out / "connectivity_graph.json"
    paths["graph"].write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    paths["nodes"] = out / "radio_nodes.geojson"
    paths["nodes"].write_text(
        json.dumps(_fc([_point(center[0], center[1], {"node": "bs_stub"})]), indent=2) + "\n", encoding="utf-8"
    )
    paths["zones"] = out / "service_zones.geojson"
    paths["zones"].write_text(json.dumps(_fc([_poly_bbox(center, 0.015)]), indent=2) + "\n", encoding="utf-8")
    paths["qos"] = out / "qos_classes.yaml"
    paths["qos"].write_text(yaml.dump({"classes": ["education", "emergency", "general"], "evidence_status": ev}), encoding="utf-8")
    paths["report"] = out / "connectivity_report.md"
    paths["report"].write_text(f"# Connectivity — {site_id}\n\nEvidence: {ev}\n", encoding="utf-8")
    return paths


def build_population(site_id: str, mode: str) -> dict[str, Path]:
    out = scene_root(site_id) / "population"
    out.mkdir(parents=True, exist_ok=True)
    ev = _evidence(mode)
    pop = {
        "categories": ["students", "teachers", "families", "small_business_owners", "community_technicians",
                       "public_service_users", "researchers", "accessibility_users", "crisis_priority_users"],
        "synthetic": True,
        "evidence_status": ev,
        "no_real_person_data": True,
    }
    devices = {
        "classes": ["student_14_5", "handheld_hybrid", "ds_xl_coder", "edge_io_wearable",
                    "community_kiosk", "teacher_admin_device", "repair_lab_device", "sensor_or_measurement_node"],
        "evidence_status": ev,
    }
    paths = {}
    for name, data, fname in [
        ("pop", pop, "synthetic_population.json"),
        ("dev", devices, "device_distribution.json"),
        ("usage", {"profiles": ["education", "workforce", "emergency"], "evidence_status": ev}, "usage_profiles.json"),
    ]:
        p = out / fname
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        paths[name] = p
    paths["privacy"] = out / "privacy_notes.md"
    paths["privacy"].write_text(f"# Privacy — {site_id}\n\nSynthetic population only. No PII.\n", encoding="utf-8")
    return paths


def build_use_cases_layer(site_id: str, mode: str) -> dict[str, Path]:
    import yaml

    profile = load_profile(site_id)
    out = scene_root(site_id) / "use_cases"
    out.mkdir(parents=True, exist_ok=True)
    ev = _evidence(mode)
    reg = {
        "site_id": site_id,
        "anchor_use_cases": profile["anchor_use_cases"],
        "resilience_use_cases": profile["resilience_use_cases"],
        "bad_day_scenarios": profile["bad_day_scenarios"],
        "evidence_status": ev,
    }
    paths = {}
    paths["json"] = out / "use_case_register.json"
    paths["json"].write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    md = "\n".join(f"- **{u['use_case_id']}**: {u['name']}" for u in profile["anchor_use_cases"])
    paths["md"] = out / "use_case_register.md"
    paths["md"].write_text(f"# Use cases — {site_id}\n\n{md}\n", encoding="utf-8")
    paths["bad"] = out / "bad_day_scenarios.md"
    paths["bad"].write_text(
        "\n".join(f"- `{b['scenario_id']}`" for b in profile["bad_day_scenarios"]) + "\n", encoding="utf-8"
    )
    from .community_benefit import community_benefit_report
    from .local_capacity import local_capacity_plan
    from .campus_metrics import compute_campus_metrics

    m = compute_campus_metrics(site_id, mode="smoke")
    paths["benefit"] = out / "community_benefit_model.md"
    paths["benefit"].write_text(
        f"# Community benefit\n\n```json\n{json.dumps(community_benefit_report(site_id, m), indent=2)}\n```\n", encoding="utf-8"
    )
    paths["capacity"] = out / "local_capacity_plan.md"
    paths["capacity"].write_text(
        f"# Local capacity\n\n```json\n{json.dumps(local_capacity_plan(site_id), indent=2)}\n```\n", encoding="utf-8"
    )
    return paths


def build_integration_stubs(site_id: str, mode: str) -> None:
    """Write waike, edge_io, ntn, ai_ran, beam_selection integration artifact stubs."""
    import yaml

    ev = _evidence(mode)
    root = scene_root(site_id)

    def _md(sub: str, name: str, body: str):
        d = root / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body, encoding="utf-8")

    _md("waike", "learning_tracks.md", f"# WAIKE — {site_id}\n\nSee waike-research-ops campus track.\n")
    _md("waike", "apprenticeship_tasks.json", json.dumps({"tasks": ["smoke_lab_1"], "evidence_status": ev}, indent=2) + "\n")
    _md("waike", "family_learning_night.md", f"# Family night — {site_id}\n")
    _md("waike", "instructor_packet.md", f"# Instructor — {site_id}\n")
    _md("waike", "capstone_brief.md", f"# Capstone — {site_id}\n")

    _md("edge_io", "measurement_plan.md", f"# Edge-IO plan — {site_id}\n")
    (root / "edge_io" / "allowed_measurements.yaml").write_text(
        yaml.dump({"allowed": ["latency_ms", "jitter_ms", "packet_loss_pct"], "evidence_status": ev}), encoding="utf-8"
    )
    (root / "edge_io" / "prohibited_measurements.yaml").write_text(
        yaml.dump({"prohibited": ["precise_gps", "student_id", "biometrics"], "evidence_status": ev}), encoding="utf-8"
    )
    _md("edge_io", "privacy_report.md", f"# Privacy — {site_id}\n")
    (root / "edge_io" / "telemetry_contract.json").write_text(
        json.dumps({"site_id": site_id, "consent": "explicit_opt_in", "evidence_status": ev}, indent=2) + "\n", encoding="utf-8"
    )

    (root / "ntn").mkdir(parents=True, exist_ok=True)
    _md("ntn", "resilience_scenario.yaml", yaml.dump({"site_id": site_id, "scenario_stub": True, "evidence_status": ev}))
    _md("ntn", "service_continuity_report.md", f"# NTN continuity — {site_id}\n")
    _md("ntn", "policy_comparison.md", f"# Policy comparison — {site_id}\n")
    (root / "ntn" / "recovery_timeline.json").write_text(
        json.dumps({"recovery_steps": ["restore_terrestrial", "ntn_window", "sync_cache"], "evidence_status": ev}, indent=2) + "\n",
        encoding="utf-8",
    )

    (root / "ai_ran").mkdir(parents=True, exist_ok=True)
    (root / "ai_ran" / "campus_ai_ran_profile.yaml").write_text(
        yaml.dump({"site_id": site_id, "traffic_classes": ["education", "emergency"], "evidence_status": ev}), encoding="utf-8"
    )
    _md("ai_ran", "policy_requirements.md", f"# AI-RAN policy — {site_id}\n")
    (root / "beam_selection").mkdir(parents=True, exist_ok=True)
    (root / "beam_selection" / "radio_profile.yaml").write_text(
        yaml.dump({"site_id": site_id, "mobility_case": "stub", "evidence_status": ev}), encoding="utf-8"
    )
    _md("beam_selection", "beam_use_case_report.md", f"# Beam use case — {site_id}\n")


def build_campus_report(site_id: str, mode: str) -> Path:
    out = scene_root(site_id) / "reports"
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_site_config(site_id)
    body = f"""# Campus report — {site_id}

| Field | Value |
|-------|-------|
| Display | {cfg.get('display_name')} |
| Role | {cfg.get('campus_role')} |
| Build mode | {mode} |
| Evidence | {_evidence(mode)} |

## Layers generated
- geo/, 3d/, connectivity/, population/, use_cases/
- waike/, edge_io/, ntn/, ai_ran/, beam_selection/

## Validation
Local partner approval: **not claimed**. Field validation: **not claimed**.
"""
    p = out / "campus_report.md"
    p.write_text(body, encoding="utf-8")
    return p


def build_scene(site_id: str, mode: str = "synthetic-fixture") -> dict[str, Any]:
    """Build full scene tree for one campus."""
    if site_id not in SITES:
        raise ValueError(f"Unknown site: {site_id}")
    build_geospatial(site_id, mode)
    build_3d(site_id, mode)
    build_connectivity(site_id, mode)
    build_population(site_id, mode)
    build_use_cases_layer(site_id, mode)
    build_integration_stubs(site_id, mode)
    report = build_campus_report(site_id, mode)
    return {"site_id": site_id, "mode": mode, "evidence_status": _evidence(mode), "report": str(report)}


def build_all_scenes(mode: str = "synthetic-fixture") -> list[dict]:
    return [build_scene(s, mode) for s in SITES]


def make_conference_artifacts() -> Path:
    out = Path("results/conference")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for s in SITES:
        rows.append(f"| {s} | {CAMPUS_GEO[s]['country']} | {CAMPUS_GEO[s]['role']} | smoke_test_only / open_data |")
    (out / "7gc_scene_table.md").write_text(
        "# 7GC scene table\n\n| site | country | role | evidence |\n|------|---------|------|----------|\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    (out / "7gc_use_case_table.md").write_text(
        "# Use case table\n\nGenerated from configs/site_profiles — see per-site use_case_register.json\n", encoding="utf-8"
    )
    (out / "7gc_evidence_maturity_table.md").write_text(
        "# Evidence maturity\n\n| site | maturity |\n|------|----------|\n"
        + "\n".join(f"| {s} | Level 1 smoke / open-data prep |" for s in SITES) + "\n",
        encoding="utf-8",
    )
    (out / "7gc_methods_summary.md").write_text(
        "# Methods\n\nProcedural scene builder + optional OSM ingest. Not field validated.\n", encoding="utf-8"
    )
    (out / "7gc_limitations.md").write_text(
        "# Limitations\n\nSynthetic fixture default; no operational 6G claim.\n", encoding="utf-8"
    )
    return out


def integration_map_doc() -> Path:
    out = Path("results/cross_repo")
    out.mkdir(parents=True, exist_ok=True)
    md = """# Cross-repo integration map

| Repo | Artifact path in scene |
|------|------------------------|
| edge-io-measurement-node | scenes/<site>/edge_io/ |
| ntn-resilience-sim | scenes/<site>/ntn/ |
| waike-research-ops | scenes/<site>/waike/ |
| spectrumx-ai-ran-gary | scenes/<site>/ai_ran/ |
| readygary-6g-beam-selection | scenes/<site>/beam_selection/ |
| gunnchos-device-os | device modes via integration |
| gunnchos-hardware-industrial-design | hardware kits via integration |
"""
    p = out / "integration_map.md"
    p.write_text(md, encoding="utf-8")
    (out / "artifact_map.json").write_text(
        json.dumps({"sites": SITES, "evidence_default": "smoke_test_only"}, indent=2) + "\n", encoding="utf-8"
    )
    return p
