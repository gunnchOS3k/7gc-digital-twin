"""AI-RAN integration map — computed Gate 2 compatibility."""
from __future__ import annotations

from pathlib import Path


def integration_status(site_id: str) -> dict:
    schema = (
        Path(__file__).resolve().parents[4]
        / "gunnchos-7gc-ai-ran-field-kit"
        / "contracts"
        / "airan_decision_bundle.v1.schema.json"
    )
    adapter = Path(__file__).resolve().parents[1] / "gate2" / "edge_ingest.py"
    return {
        "repo": "spectrumx-ai-ran-gary",
        "site_id": site_id,
        "export_contract": "gunnchos.airan_decision_bundle",
        "input_contract": "gunnchos.twin_state_bundle",
        "status": "gate2_compatible" if schema.is_file() and adapter.is_file() else "incompatible",
        "profile": f"configs/campus_ai_ran_profiles/{site_id}.yaml",
    }
