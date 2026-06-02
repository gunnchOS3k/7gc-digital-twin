"""Campus operational metrics (smoke composites)."""
from __future__ import annotations

import hashlib

from .site_profiles import load_profile


def _seed_score(site_id: str, salt: str) -> float:
    h = hashlib.sha256(f"{site_id}:{salt}".encode()).hexdigest()
    return round(int(h[:8], 16) / 0xFFFFFFFF, 4)


def compute_campus_metrics(site_id: str, mode: str = "smoke") -> dict:
    p = load_profile(site_id)
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
    return {
        "site_id": site_id,
        "mode": mode,
        "evidence_status": "smoke_test_only",
        "digital_inclusion_readiness": round(max(0.2, 1.0 - n_barriers * 0.04), 4),
        "access_barrier_score": round(min(1.0, n_barriers * 0.07), 4),
        "affordability_pressure": _seed_score(site_id, "afford"),
        "power_resilience_risk": _seed_score(site_id, "power"),
        "privacy_data_harm_risk": _seed_score(site_id, "privacy"),
        "local_capacity_readiness": _seed_score(site_id, "capacity"),
        "community_governance_readiness": _seed_score(site_id, "gov"),
        "evidence_maturity_level": 1 if mode == "smoke" else 2,
        "needs_local_validation": True,
    }
