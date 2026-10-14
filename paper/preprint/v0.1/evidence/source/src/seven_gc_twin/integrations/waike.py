"""WAIKE integration map."""
from __future__ import annotations


def integration_status(site_id: str) -> dict:
    return {"repo": "waike-research-ops", "site_id": site_id, "track_config": f"configs/campus_learning_tracks/{site_id}.yaml", "status": "smoke_contract"}
