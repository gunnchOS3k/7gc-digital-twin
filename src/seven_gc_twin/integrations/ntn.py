"""NTN integration map."""
from __future__ import annotations


def integration_status(site_id: str) -> dict:
    return {"repo": "ntn-resilience-sim", "site_id": site_id, "scenario_prefix": site_id, "status": "smoke_contract"}
