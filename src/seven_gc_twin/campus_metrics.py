"""Campus operational metrics (synthetic composites for RQ1 profiles/benchmarks).

Workload, compute, radio, failure, and mobility families are derived from
documented YAML stubs and synthetic user draws. They are **not** RF/device
measurements.
"""
from __future__ import annotations

import hashlib
from typing import Any

from .metrics import energy_per_bit_joules, jains_fairness, spectral_efficiency_bps_hz
from .provenance import stamp
from .scenario_loader import load_scenario
from .site_profiles import load_profile
from .config.schema import FLAGSHIP_SITE_ID, METRIC_FAMILIES


def _seed_score(site_id: str, salt: str) -> float:
    h = hashlib.sha256(f"{site_id}:{salt}".encode()).hexdigest()
    return round(int(h[:8], 16) / 0xFFFFFFFF, 4)


def _workload_metrics(users: list[dict[str, Any]]) -> dict[str, Any]:
    demands = [float(u.get("demand_mbps", 0.0)) for u in users]
    n = max(len(demands), 1)
    mean_d = sum(demands) / n
    return {
        "n_synthetic_users": len(users),
        "mean_demand_mbps": round(mean_d, 4),
        "p95_demand_mbps": round(sorted(demands)[int(0.95 * (n - 1))] if demands else 0.0, 4),
        "jains_fairness_on_demand": round(jains_fairness(demands), 4),
        "evidence_status": "synthetic_fixture",
    }


def _mobility_metrics(users: list[dict[str, Any]], site: dict[str, Any]) -> dict[str, Any]:
    mix = [u.get("mobility", "static") for u in users]
    n = max(len(mix), 1)
    pedestrian = sum(1 for m in mix if m == "pedestrian") / n
    device_mix = site.get("device_mix") or {}
    return {
        "pedestrian_fraction": round(pedestrian, 4),
        "static_fraction": round(1.0 - pedestrian, 4),
        "configured_mobile_pct": device_mix.get("mobile_pct"),
        "evidence_status": "synthetic_fixture",
    }


def _radio_metrics(site: dict[str, Any]) -> dict[str, Any]:
    radio = site.get("radio") or {}
    sinr = float(radio.get("sinr_db_stub", 10.0))
    bands = (site.get("spectrum") or site.get("spectrum_constraints") or {}).get("bands_ghz", [])
    return {
        "sinr_db_stub": sinr,
        "spectral_efficiency_bps_hz_stub": round(spectral_efficiency_bps_hz(sinr), 4),
        "bands_ghz_planning": bands,
        "note": "planning stub — not a channel sounding result",
        "evidence_status": "synthetic_fixture",
    }


def _compute_metrics(site: dict[str, Any], users: list[dict[str, Any]]) -> dict[str, Any]:
    energy = site.get("energy_constraints") or {}
    power_w = float(energy.get("power_w_stub", 5.0))
    demand_bps = max(sum(float(u.get("demand_mbps", 0.0)) for u in users), 0.001) * 1e6
    return {
        "power_w_stub": power_w,
        "energy_per_bit_j_stub": round(energy_per_bit_joules(power_w, demand_bps), 12),
        "note": "energy model uses configured stubs, not measured device draw",
        "evidence_status": "synthetic_fixture",
    }


def _failure_metrics(profile: dict[str, Any]) -> dict[str, Any]:
    bad = profile.get("bad_day_scenarios") or []
    resilience = profile.get("resilience_barriers") or []
    return {
        "named_bad_day_count": len(bad),
        "resilience_barrier_count": len(resilience),
        "needs_local_validation": True,
        "evidence_status": "scenario_library_only",
    }


def compute_campus_metrics(site_id: str, mode: str = "smoke") -> dict:
    p = load_profile(site_id)
    scenario = load_scenario(site_id)
    site = scenario["site"]
    users = scenario["users"]
    n_barriers = sum(
        len(p.get(k, []))
        for k in (
            "access_barriers",
            "affordability_barriers",
            "device_barriers",
            "skills_barriers",
            "trust_privacy_barriers",
            "power_energy_barriers",
            "resilience_barriers",
        )
    )
    families = {
        "workload": _workload_metrics(users),
        "compute": _compute_metrics(site, users),
        "radio": _radio_metrics(site),
        "failure": _failure_metrics(p),
        "mobility": _mobility_metrics(users, site),
        "inclusion": {
            "digital_inclusion_readiness": round(max(0.2, 1.0 - n_barriers * 0.04), 4),
            "access_barrier_score": round(min(1.0, n_barriers * 0.07), 4),
            "affordability_pressure": _seed_score(site_id, "afford"),
            "power_resilience_risk": _seed_score(site_id, "power"),
            "privacy_data_harm_risk": _seed_score(site_id, "privacy"),
            "local_capacity_readiness": _seed_score(site_id, "capacity"),
            "community_governance_readiness": _seed_score(site_id, "gov"),
        },
    }
    return {
        "site_id": site_id,
        "is_flagship": site_id == FLAGSHIP_SITE_ID or bool(site.get("is_flagship")),
        "scenario_environment_not_community_deployment": True,
        "mode": mode,
        "evidence_status": "smoke_test_only" if mode in {"smoke", "synthetic-fixture", "toy"} else mode,
        "metric_families": list(METRIC_FAMILIES),
        **families["inclusion"],
        "families": families,
        "evidence_maturity_level": 1 if mode in {"smoke", "synthetic-fixture", "toy"} else 2,
        "needs_local_validation": True,
        "provenance": stamp(
            artifact_kind="campus_metrics",
            site_id=site_id,
            mode=mode,
            extra={"n_users": len(users), "n_barriers": n_barriers},
        ),
    }
