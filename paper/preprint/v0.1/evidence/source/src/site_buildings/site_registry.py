"""Site registry for 7GC campus building digital twin."""
from __future__ import annotations

SITE_IDS = ["gary", "ghana", "guyana", "gaza", "geelong", "graham_land", "germany"]

SITE_DISPLAY = {
    "gary": "WAIKE Gary UPNOW",
    "ghana": "WAIKE Ghana UPNOW",
    "guyana": "WAIKE Guyana UPNOW",
    "gaza": "WAIKE Gaza UPNOW",
    "geelong": "WAIKE Geelong UPNOW",
    "graham_land": "WAIKE Graham Land UPNOW",
    "germany": "WAIKE Germany UPNOW",
}

SHARED_ROOMS = [
    "welcome_intake",
    "flexible_classroom",
    "device_bar",
    "hardware_repair_lab",
    "networking_cyber_lab",
    "ai_cloud_studio",
    "career_portfolio_studio",
    "community_room",
    "staff_mentor_workspace",
    "secure_storage",
    "quiet_decompression",
    "hybrid_learning_corner",
    "server_comms_closet",
    "mechanical_electrical_zone",
    "public_exhibit_wall",
]

EXTRA_ROOMS = {
    "gary": ["civic_tech_studio", "ai_ran_edge_lab", "small_business_help_desk"],
    "ghana": ["mobile_first_studio", "repair_refurb_bench", "entrepreneurship_clinic"],
    "guyana": ["climate_gis_studio", "river_logistics_studio", "flood_literacy_wall"],
    "gaza": ["offline_kit_station", "device_clinic", "teacher_support_station"],
    "geelong": ["design_build_studio", "manufacturing_sensor_bench", "design_critique_room"],
    "graham_land": ["polar_digital_twin_studio", "ntn_satellite_lab", "field_safety_classroom"],
    "germany": ["apprenticeship_studio", "mechatronics_lab", "industrial_cyber_range"],
}


def get_site(site_id: str) -> dict:
    if site_id not in SITE_IDS:
        raise KeyError(site_id)
    rooms = SHARED_ROOMS + EXTRA_ROOMS.get(site_id, [])
    return {
        "site_id": site_id,
        "display_name": SITE_DISPLAY[site_id],
        "rooms": rooms,
        "conceptual_only": site_id in ("graham_land",),
        "privacy_sensitive": site_id == "gaza",
    }
