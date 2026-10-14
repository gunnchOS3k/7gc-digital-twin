"""Power and connectivity assumptions."""
from __future__ import annotations

from site_buildings.site_registry import get_site

POWER_DEFAULTS = {
    "gary": {"backup": "UPS + generator concept", "edge_cache": True},
    "ghana": {"backup": "solar + battery concept", "edge_cache": True},
    "guyana": {"backup": "elevated gear + flood-aware", "edge_cache": True},
    "gaza": {"backup": "solar/battery learning kits", "edge_cache": True},
    "geelong": {"backup": "industrial UPS concept", "edge_cache": True},
    "graham_land": {"backup": "simulated polar power", "edge_cache": True},
    "germany": {"backup": "industrial continuity", "edge_cache": True},
}


def power_model(site_id: str) -> dict:
    site = get_site(site_id)
    defaults = POWER_DEFAULTS.get(site_id, {})
    return {
        "site_id": site_id,
        "wired_ethernet_fiber": True,
        "wifi_ap_per_zone": True,
        "student_network_segmented": True,
        "lab_network_isolated": True,
        **defaults,
        "evidence_status": "design assumption",
        "disclaimer": "research simulation only — not operational service",
    }
