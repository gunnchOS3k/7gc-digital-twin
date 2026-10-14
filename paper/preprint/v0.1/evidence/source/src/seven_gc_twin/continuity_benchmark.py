"""Analyze frozen Device OS continuity profiles against Gary scenarios.

Levels are re-derived from stored orchestrator snapshots using the same rule as
`gunnchos_device_os.service_continuity.evaluate.classify_continuity`. Numbers
come from the frozen JSON; this module does not invent RF measurements.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .campus_metrics import compute_campus_metrics
from .config.schema import ALL_SITE_IDS
from .site_profiles import load_profile

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILES = ROOT / "fixtures" / "device_os" / "SERVICE_CONTINUITY_PROFILES.json"
PROVENANCE = ROOT / "fixtures" / "device_os" / "PROVENANCE.json"

DEFAULT_GARY_MAP = {
    "neighborhood_outage": "jam_wifi_offline_fallback",
    "storm_congestion": "degraded_wifi",
    "school_bandwidth_collapse": "degraded_wifi",
    "library_hotspot_overload": "degraded_wifi",
    "smb_payment_system_down": "force_offline",
}

LEVEL_ORDER = {"failed": 0, "min_useful": 1, "degraded": 2, "target": 3}


def classify_continuity(orchestrator_state: str, *, offline_covers_workload: bool) -> str:
    if orchestrator_state == "connected":
        return "target"
    if orchestrator_state in {"degraded", "transitioning"}:
        return "degraded"
    if orchestrator_state == "offline" and offline_covers_workload:
        return "min_useful"
    return "failed"


def load_profiles(path: Path | None = None) -> dict[str, Any]:
    src = path or DEFAULT_PROFILES
    return json.loads(src.read_text(encoding="utf-8"))


def _scenario_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for cls, prof in (bundle.get("profiles") or {}).items():
        for sc in prof.get("benchmark_scenarios") or []:
            stored = sc.get("continuity_level")
            derived = classify_continuity(
                str(sc.get("orchestrator_state") or ""),
                offline_covers_workload=bool(sc.get("offline_covers_workload")),
            )
            rows.append(
                {
                    "research_class": cls,
                    "device_id": sc.get("device_id"),
                    "scenario_id": sc.get("scenario_id"),
                    "workload": sc.get("workload"),
                    "orchestrator_state": sc.get("orchestrator_state"),
                    "active_bearer": sc.get("active_bearer"),
                    "offline_covers_workload": bool(sc.get("offline_covers_workload")),
                    "continuity_level_stored": stored,
                    "continuity_level_derived": derived,
                    "level_match": stored == derived,
                    "below_min_useful": derived == "failed",
                    "at_min_useful": derived == "min_useful",
                }
            )
    return rows


def analyze_continuity(
    *,
    mapping: dict[str, str] | None = None,
    site_id: str = "gary",
    profiles_path: Path | None = None,
) -> dict[str, Any]:
    bundle = load_profiles(profiles_path)
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8")) if PROVENANCE.exists() else {}
    rows = _scenario_rows(bundle)
    gary_map = mapping or DEFAULT_GARY_MAP
    profile = load_profile(site_id)
    overlay = []
    for bad in profile.get("bad_day_scenarios") or []:
        gary_sid = bad["scenario_id"]
        bearer_sid = gary_map.get(gary_sid)
        for cls, prof in (bundle.get("profiles") or {}).items():
            match = [
                s
                for s in prof.get("benchmark_scenarios") or []
                if s.get("scenario_id") == bearer_sid
            ]
            if not match:
                continue
            sc = match[0]
            derived = classify_continuity(
                str(sc.get("orchestrator_state") or ""),
                offline_covers_workload=bool(sc.get("offline_covers_workload")),
            )
            overlay.append(
                {
                    "gary_scenario_id": gary_sid,
                    "mapped_bearer_stress": bearer_sid,
                    "research_class": cls,
                    "workload": sc.get("workload"),
                    "continuity_level": derived,
                    "below_min_useful": derived == "failed",
                    "at_min_useful": derived == "min_useful",
                    "active_bearer": sc.get("active_bearer"),
                    "mapping_assumption": True,
                }
            )
    level_counts: dict[str, dict[str, int]] = {}
    for cls in bundle.get("research_classes") or []:
        level_counts[cls] = dict(Counter(r["continuity_level_derived"] for r in rows if r["research_class"] == cls))
    failed = [r for r in rows if r["below_min_useful"]]
    min_useful = [r for r in rows if r["at_min_useful"]]
    mismatches = [r for r in rows if not r["level_match"]]
    degraded_label_still_target = [
        r
        for r in rows
        if r["scenario_id"] == "degraded_wifi" and r["continuity_level_derived"] == "target"
    ]
    return {
        "schema": bundle.get("schema"),
        "content_digest_sha256": bundle.get("content_digest_sha256"),
        "expected_digest_sha256": provenance.get("content_digest_sha256"),
        "digest_match": bundle.get("content_digest_sha256") == provenance.get("content_digest_sha256"),
        "level_rederive_all_match": not mismatches,
        "n_mismatch": len(mismatches),
        "n_scenarios": len(rows),
        "level_counts_by_class": level_counts,
        "failed_cases": failed,
        "min_useful_cases": min_useful,
        "classes_that_failed": sorted({r["research_class"] for r in failed}),
        "classes_never_failed": sorted(
            {
                cls
                for cls in (bundle.get("research_classes") or [])
                if cls not in {r["research_class"] for r in failed}
            }
        ),
        "degraded_wifi_still_target": degraded_label_still_target,
        "gary_overlay": overlay,
        "gary_overlay_below_min_useful": [r for r in overlay if r["below_min_useful"]],
        "scenario_rows": rows,
        "workload_offline_coverage": {
            cls: (prof.get("workload_offline_coverage") or {})
            for cls, prof in (bundle.get("profiles") or {}).items()
        },
        "claim_boundary": bundle.get("claim_boundary"),
        "evidence_status": "synthetic_fixture",
    }


def site_metric_panel(seeds: list[int], mode: str = "synthetic-fixture") -> dict[str, Any]:
    """Seeded campus families for flagship + comparative scenario environments."""
    per_seed = []
    for seed in seeds:
        families = compute_campus_metrics("gary", mode=mode, seed=seed)
        wl = families["families"]["workload"]
        mob = families["families"]["mobility"]
        per_seed.append(
            {
                "seed": seed,
                "mean_demand_mbps": wl["mean_demand_mbps"],
                "p95_demand_mbps": wl["p95_demand_mbps"],
                "jains_fairness_on_demand": wl["jains_fairness_on_demand"],
                "n_synthetic_users": wl["n_synthetic_users"],
                "pedestrian_fraction": mob["pedestrian_fraction"],
                "radio_evidence_status": families["families"]["radio"]["evidence_status"],
                "sinr_db_stub": families["families"]["radio"]["sinr_db_stub"],
            }
        )
    demands = [r["mean_demand_mbps"] for r in per_seed]
    sites = []
    for sid in ALL_SITE_IDS:
        m = compute_campus_metrics(sid, mode=mode, seed=seeds[0] if seeds else 42)
        sites.append(
            {
                "site_id": sid,
                "is_flagship": m.get("is_flagship"),
                "digital_inclusion_readiness": m.get("digital_inclusion_readiness"),
                "access_barrier_score": m.get("access_barrier_score"),
                "affordability_pressure": m.get("affordability_pressure"),
                "power_resilience_risk": m.get("power_resilience_risk"),
                "mean_demand_mbps": m["families"]["workload"]["mean_demand_mbps"],
                "evidence_status": m["families"]["radio"]["evidence_status"],
            }
        )
    return {
        "gary_seed_runs": per_seed,
        "gary_mean_demand_mbps_min": min(demands) if demands else None,
        "gary_mean_demand_mbps_max": max(demands) if demands else None,
        "gary_mean_demand_mbps_range": round(max(demands) - min(demands), 4) if demands else None,
        "site_inclusion": sites,
        "evidence_status": "synthetic_fixture",
    }
