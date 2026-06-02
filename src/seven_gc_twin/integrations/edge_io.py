"""Edge-IO integration map (contract stub)."""
from __future__ import annotations


def integration_status(site_id: str) -> dict:
    return {
        "repo": "edge-io-measurement-node",
        "site_id": site_id,
        "export_contract": "sanitized_measurements.json",
        "status": "smoke_contract",
    }
