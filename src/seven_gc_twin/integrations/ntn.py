"""NTN integration map — computed Gate 2 compatibility."""
from __future__ import annotations

from pathlib import Path


def integration_status(site_id: str) -> dict:
    schema = (
        Path(__file__).resolve().parents[4]
        / "gunnchos-7gc-ai-ran-field-kit"
        / "contracts"
        / "resilience_decision_bundle.v1.schema.json"
    )
    return {
        "repo": "ntn-resilience-sim",
        "site_id": site_id,
        "export_contract": "gunnchos.resilience_decision_bundle",
        "input_contract": "gunnchos.twin_state_bundle + gunnchos.airan_decision_bundle",
        "status": "gate2_compatible" if schema.is_file() else "incompatible",
        "scenario_prefix": site_id,
    }
