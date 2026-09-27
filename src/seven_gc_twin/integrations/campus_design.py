"""Campus design bundle → canonical 7GC twin state."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SITE_IDS = (
    "gary",
    "ghana",
    "guyana",
    "geelong",
    "germany",
    "gaza",
    "graham_land",
)

SLUG_TO_SITE = {
    "gary": "gary",
    "ghana": "ghana",
    "guyana": "guyana",
    "geelong": "geelong",
    "germany": "germany",
    "gaza": "gaza",
    "graham-land": "graham_land",
    "graham_land": "graham_land",
}


def _bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(_bytes(obj)).hexdigest()


def normalize_site_id(value: str) -> str:
    key = value.strip().lower().replace(" ", "_")
    if key not in SLUG_TO_SITE:
        raise ValueError(f"Unknown campus identity: {value}")
    return SLUG_TO_SITE[key]


def adapt_campus_design_bundle(
    design: dict[str, Any],
    *,
    producer_commit: str = "0" * 40,
) -> dict[str, Any]:
    """Create/augment twin state from a campus design projection.

    Does not invent surveyed geometry. If geometry_fidelity is
    AUTHORED_PLANNING_LAYOUT, that class is propagated.
    """
    site_id = normalize_site_id(str(design.get("site_id") or design.get("campus_slug")))
    fidelity = design.get("geometry_fidelity", "AUTHORED_PLANNING_LAYOUT")
    if fidelity == "AS_BUILT_SURVEYED":
        raise ValueError("as-built surveyed geometry requires partner evidence")
    n_users = int((design.get("aggregate_demand") or {}).get("values", {}).get("users_proxy", 16))
    latency = 18.0
    if site_id == "gaza":
        latency = 42.0
    elif site_id == "graham_land":
        latency = 55.0
    zones = design.get("zones") or []
    commit = producer_commit if len(producer_commit) == 40 else "0" * 40
    return {
        "schema_name": "gunnchos.twin_state_bundle",
        "schema_version": "1.0.0",
        "run_id": f"mlv-campus-twin-v2-{site_id}",
        "site_id": site_id,
        "source_measurement": {
            "summary": {
                "n_samples": max(len(zones), 1),
                "mean_latency_ms": latency,
                "mean_jitter_ms": 3.0,
                "mean_packet_loss_pct": 0.4,
                "mean_upload_mbps": 12.0,
                "mean_download_mbps": 48.0,
                "dominant_network_type": "wifi",
                "workload_profile": "learn",
                "service_profile": "learn_continuity",
            },
            "sha256": sha256_obj({"run": design.get("run_id"), "site": site_id}),
            "producer_repository": "edge-io-measurement-node",
            "producer_commit": commit,
        },
        "service_demand": {
            "values": {
                "service_profile": "learn_continuity",
                "geometry_fidelity": fidelity,
                "source_manifest_sha256": design.get("source_manifest_sha256"),
                "rooms_zones": [z.get("campus_requirement_id") for z in zones],
                "material_assumptions": [z.get("material_assumption") for z in zones],
                "service_intents": design.get("service_intents"),
                "candidate_infrastructure": [
                    n.get("node_id") for n in design.get("candidate_infrastructure", [])
                ],
            },
            "origin": "configured",
        },
        "user_demands": [
            {
                "user_class": "learn",
                "priority": 2,
                "latency_budget_ms": 150.0,
                "bandwidth_mbps": 10.0,
                "origin": "configured",
            }
        ],
        "connectivity_candidates": [
            {
                "network": "terrestrial",
                "available": site_id not in {"gaza", "graham_land"},
                "estimated_latency_ms": latency,
                "estimated_capacity_mbps": 48.0,
                "origin": "configured",
            },
            {
                "network": "local_edge_wifi",
                "available": True,
                "estimated_latency_ms": 12.0,
                "estimated_capacity_mbps": 40.0,
                "origin": "configured",
            },
            {
                "network": "degraded_local",
                "available": True,
                "estimated_latency_ms": latency * 1.4,
                "estimated_capacity_mbps": 12.0,
                "origin": "configured",
            },
            {
                "network": "ntn_fallback",
                "available": True,
                "estimated_latency_ms": 80.0 if site_id == "graham_land" else 45.0,
                "estimated_capacity_mbps": 5.0,
                "origin": "configured",
            },
            {
                "network": "device_to_device",
                "available": False,
                "estimated_latency_ms": None,
                "estimated_capacity_mbps": None,
                "origin": "missing",
            },
            {
                "network": "offline_continuation",
                "available": True,
                "estimated_latency_ms": 0.0,
                "estimated_capacity_mbps": 0.0,
                "origin": "configured",
            },
        ],
        "network_state": {
            "values": {
                "dominant_network_type": "wifi",
                "mean_latency_ms": latency,
                "geometry_fidelity": fidelity,
            },
            "origin": "inferred",
        },
        "spectrum_availability": design.get("spectrum")
        or {"values": {"budget_mhz": 20.0}, "origin": "configured"},
        "compute_availability": design.get("compute")
        or {"values": {"local_edge": True}, "origin": "configured"},
        "mobility_state": design.get("mobility")
        or {"values": {"class": "low_named_zone"}, "origin": "configured"},
        "blockage_state": design.get("blockage")
        or {"values": {"scenario": "interior_partitions"}, "origin": "configured"},
        "energy_constraints": design.get("energy")
        or {"values": {"budget_j": 120.0}, "origin": "configured"},
        "outage_state": design.get("outage")
        or {"values": {"terrestrial_outage": False}, "origin": "configured"},
        "privacy_constraints": {
            "values": design.get("privacy")
            or {
                "contains_direct_identifiers": False,
                "contains_person_path": False,
            },
            "origin": "configured",
        },
        "continuity_requirements": design.get("continuity")
        or {"values": {"class": "degraded_ok"}, "origin": "configured"},
        "uncertainty": design.get("uncertainty")
        or {
            "overall": "high",
            "notes": "AUTHORED_PLANNING_LAYOUT; not surveyed geometry.",
        },
        "missing_data_flags": ["surveyed_geometry", "measured_occupancy"],
        "field_provenance": {
            "fields": {
                "network_state": "inferred",
                "service_demand": "configured",
                "geometry_fidelity": "configured",
                "evidence_class": str(design.get("evidence_class", "SIMULATED")).lower(),
            }
        },
        "scenario_provenance": {
            "transformer": "seven_gc_twin.integrations.campus_design.v1",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "notes": "No surveyed geometry invented.",
        },
        "configuration_hash": sha256_obj(
            {
                "site_id": site_id,
                "source": design.get("source_manifest_sha256"),
                "geometry": fidelity,
            }
        ),
        "evidence_level": "synthetic",
        "producer": {"repository": "7gc-digital-twin", "commit": commit},
        "n_users": max(n_users, 1),
        "service_profile": "learn_continuity",
    }


def _field_kit_closed_loop():
    root = Path(__file__).resolve()
    for parent in root.parents:
        candidate = parent / "field-kit"
        if (candidate / "control_plane" / "closed_loop.py").is_file():
            sys.path.insert(0, str(candidate))
            from control_plane.closed_loop import run_seven_campus_loop

            return run_seven_campus_loop
    return None


def run_mlv_to_7gc_adapter(source_manifest_sha256: str | None = None) -> dict[str, Any]:
    runner = _field_kit_closed_loop()
    if runner is None:
        raise RuntimeError("field-kit closed_loop sibling is required for the 7/7 adapter proof")
    kwargs = {}
    if source_manifest_sha256:
        kwargs["source_manifest_sha256"] = source_manifest_sha256
    report = runner(**kwargs)
    twins = []
    for result in report["results"]:
        twin = adapt_campus_design_bundle(result["design"])
        if twin["service_demand"]["values"]["geometry_fidelity"] != "AUTHORED_PLANNING_LAYOUT":
            raise RuntimeError("geometry fidelity not propagated")
        twins.append(twin)
    return {
        "MLV_TO_7GC_ADAPTER_PASS": f"{len(twins)}/7",
        "twins": twins,
        "campuses": [t["site_id"] for t in twins],
    }
