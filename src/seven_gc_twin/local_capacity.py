"""Local capacity planning (smoke)."""
from __future__ import annotations

from .site_profiles import load_profile


def local_capacity_plan(site_id: str) -> dict:
    p = load_profile(site_id)
    roles = p.get("required_local_steering_circle_roles", [])
    partners = p.get("local_partner_types_needed", [])
    return {
        "site_id": site_id,
        "steering_roles": roles,
        "partner_types": partners,
        "local_governance": p.get("local_governance"),
        "readiness_score": min(1.0, 0.35 + 0.08 * len(roles)),
        "evidence_to_collect": p.get("evidence_to_collect", []),
        "evidence_status": "smoke_test_only",
        "needs_local_validation": True,
    }
