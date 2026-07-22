"""Edge-IO integration map — status computed from Gate 2 contract availability."""
from __future__ import annotations

from pathlib import Path


def integration_status(site_id: str) -> dict:
    schema = (
        Path(__file__).resolve().parents[4]
        / "gunnchos-7gc-ai-ran-field-kit"
        / "contracts"
        / "edge_measurement_batch.v1.schema.json"
    )
    ingest = Path(__file__).resolve().parents[1] / "gate2" / "edge_ingest.py"
    compatible = schema.is_file() and ingest.is_file()
    return {
        "repo": "edge-io-measurement-node",
        "site_id": site_id,
        "export_contract": "gunnchos.edge_measurement_batch",
        "schema_path": str(schema) if schema.is_file() else None,
        "status": "gate2_compatible" if compatible else "incompatible",
        "compatibility_tests": [
            "seven_gc ingest-edge",
            "seven_gc build-twin-state",
            "contract validation against field-kit schema",
        ],
    }
