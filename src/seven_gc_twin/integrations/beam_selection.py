"""Beam selection integration map."""
from __future__ import annotations


def integration_status(site_id: str) -> dict:
    return {"repo": "readygary-6g-beam-selection", "site_id": site_id, "radio_profile": f"configs/campus_radio_profiles/{site_id}.yaml", "status": "smoke_contract"}
