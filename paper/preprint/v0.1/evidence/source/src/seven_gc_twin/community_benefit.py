"""Community benefit scoring (smoke composites)."""
from __future__ import annotations

from .site_profiles import load_profile


def community_benefit_report(site_id: str, metrics: dict) -> dict:
    p = load_profile(site_id)
    barriers = len(p.get("access_barriers", [])) + len(p.get("affordability_barriers", []))
    inclusion = max(0.0, min(1.0, metrics.get("digital_inclusion_readiness", 0.5)))
    return {
        "site_id": site_id,
        "campus_role": p["campus_role"],
        "digital_divide_context": p["digital_divide_context"],
        "barrier_count": barriers,
        "digital_inclusion_readiness": inclusion,
        "community_data_rights": p.get("community_data_rights"),
        "guardrails": p.get("no_foreign_savior_guardrails", []),
        "evidence_status": "smoke_test_only",
        "needs_local_validation": True,
    }
