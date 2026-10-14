"""Evidence and non-claim flags."""
from __future__ import annotations

from site_buildings.site_registry import get_site


def evidence_flags(site_id: str) -> dict:
    site = get_site(site_id)
    flags = {
        "conceptual_only_not_for_construction": True,
        "requires_architect_engineer_review": True,
        "research_simulation_only": True,
    }
    if site.get("conceptual_only"):
        flags["no_antarctic_construction_claim"] = True
        flags["polar_program_review_required"] = True
    if site.get("privacy_sensitive"):
        flags["no_sensitive_location_publish"] = True
        flags["child_protection_review_required"] = True
    return {"site_id": site_id, "flags": flags}
