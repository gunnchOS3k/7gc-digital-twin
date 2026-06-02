"""Device OS integration map."""
from __future__ import annotations


def integration_status(site_id: str) -> dict:
    return {"repo": "gunnchos-device-os", "site_id": site_id, "mode_config": f"configs/campus_device_modes/{site_id}.yaml", "status": "smoke_contract"}
