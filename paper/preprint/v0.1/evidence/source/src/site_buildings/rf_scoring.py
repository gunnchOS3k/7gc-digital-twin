"""RF/signal scoring — AP per zone, not wall leakage."""
from __future__ import annotations


def rf_tradeoff(room: str, acoustic_target: str = "moderate") -> dict:
    lab_rooms = {"networking_cyber_lab", "ntn_satellite_lab", "industrial_cyber_range", "ai_ran_edge_lab"}
    return {
        "room": room,
        "ap_in_zone": True,
        "rely_on_wall_leakage": False,
        "wired_backbone": True,
        "rf_pass_through_zone": room in lab_rooms,
        "acoustic_target": acoustic_target,
        "evidence_status": "design assumption",
    }
