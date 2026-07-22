"""Edge-IO → 7GC adapters and twin-state construction."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from seven_gc_twin.gate2.common import (
    canonical_json_bytes,
    git_commit,
    load_json,
    load_validator,
    resolve_schema_dir,
    sha256_bytes,
    sha256_file,
    write_json,
)

PROHIBITED_KEYS = {
    "email",
    "phone",
    "phone_number",
    "student_id",
    "imei",
    "imsi",
    "mac",
    "mac_address",
    "latitude",
    "longitude",
    "gps",
    "advertising_id",
    "serial_number",
    "persistent_device_id",
}


def _strip_prohibited(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: _strip_prohibited(v)
            for k, v in obj.items()
            if k.lower() not in PROHIBITED_KEYS
        }
    if isinstance(obj, list):
        return [_strip_prohibited(x) for x in obj]
    return obj


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


class EdgeIOAdapter:
    def __init__(self, path: Path, schema_dir: Path | None = None) -> None:
        self.path = Path(path)
        self.schema_dir = resolve_schema_dir(schema_dir)
        self.document: dict[str, Any] | None = None
        self.input_sha256: str | None = None

    def load(self, path: Path | None = None) -> dict[str, Any]:
        target = Path(path) if path is not None else self.path
        self.path = target
        self.input_sha256 = sha256_file(target)
        self.document = load_json(target)
        return self.document

    def validate(self) -> None:
        if self.document is None:
            self.load()
        assert self.document is not None
        mod = load_validator(self.schema_dir)
        mod.validate_document(
            self.document,
            self.schema_dir,
            expected_schema_name="gunnchos.edge_measurement_batch",
            enforce_privacy=True,
        )
        producer = self.document.get("producer") or {}
        if not producer.get("commit"):
            raise ValueError("Edge-IO batch missing producer.commit")

    def verify_ids(self, run_id: str, site_id: str) -> None:
        assert self.document is not None
        if self.document.get("run_id") != run_id:
            raise ValueError(
                f"run_id mismatch: edge={self.document.get('run_id')!r} expected={run_id!r}"
            )
        if self.document.get("site_id") != site_id:
            raise ValueError(
                f"site_id mismatch: edge={self.document.get('site_id')!r} expected={site_id!r}"
            )

    def to_twin_observations(self) -> list[dict[str, Any]]:
        assert self.document is not None
        cleaned = _strip_prohibited(self.document)
        return list(cleaned.get("measurements") or [])


class AIRANAdapter:
    def write_input(self, twin_state: dict[str, Any], output: Path) -> Path:
        return write_json(output, twin_state)


class NTNAdapter:
    def write_input(
        self,
        twin_state: dict[str, Any],
        airan_decision: dict[str, Any],
        output: Path,
    ) -> Path:
        return write_json(
            output,
            {
                "twin_state": twin_state,
                "airan_decision": airan_decision,
            },
        )


def _config_for_hash(site_id: str, run_id: str) -> dict[str, Any]:
    return {
        "transformer": "seven_gc_twin.gate2.edge_ingest.v1",
        "site_id": site_id,
        "run_id": run_id,
        "mapping_version": "1.0.0",
    }


def build_twin_state(
    adapter: EdgeIOAdapter,
    *,
    run_id: str,
    site_id: str,
) -> dict[str, Any]:
    adapter.validate()
    adapter.verify_ids(run_id, site_id)
    assert adapter.document is not None
    assert adapter.input_sha256 is not None

    observations = adapter.to_twin_observations()
    if not observations:
        raise ValueError("No measurements to aggregate")

    lat = [float(m["latency_ms"]) for m in observations]
    jit = [float(m["jitter_ms"]) for m in observations]
    loss = [float(m["packet_loss_pct"]) for m in observations]
    up = [float(m["upload_mbps"]) for m in observations]
    down = [float(m["download_mbps"]) for m in observations]
    nets = Counter(str(m.get("network_type", "unknown")) for m in observations)
    dominant = nets.most_common(1)[0][0]
    workload = adapter.document["workload"]["profile"]
    service = adapter.document["workload"]["service_profile"]

    mean_latency = _mean(lat)
    terrestrial_up = mean_latency < 200 and _mean(loss) < 20 and dominant != "unknown"
    local_edge_available = _mean([float(m["local_edge_response_ms"]) for m in observations]) < 50

    cfg = _config_for_hash(site_id, run_id)
    configuration_hash = sha256_bytes(canonical_json_bytes(cfg))

    twin = {
        "schema_name": "gunnchos.twin_state_bundle",
        "schema_version": "1.0.0",
        "run_id": run_id,
        "site_id": site_id,
        "source_measurement": {
            "summary": {
                "n_samples": len(observations),
                "mean_latency_ms": mean_latency,
                "mean_jitter_ms": _mean(jit),
                "mean_packet_loss_pct": _mean(loss),
                "mean_upload_mbps": _mean(up),
                "mean_download_mbps": _mean(down),
                "dominant_network_type": dominant,
                "workload_profile": workload,
                "service_profile": service,
            },
            "sha256": adapter.input_sha256,
            "producer_repository": adapter.document["producer"]["repository"],
            "producer_commit": adapter.document["producer"]["commit"],
        },
        "service_demand": {
            "values": {
                "service_profile": service,
                "workload_profile": workload,
                "latency_budget_ms": 80.0 if workload == "create" else 150.0 if workload == "learn" else 300.0,
            },
            "origin": "inferred",
        },
        "user_demands": [
            {
                "user_class": workload,
                "priority": 1 if workload == "create" else 2 if workload == "learn" else 3,
                "latency_budget_ms": 80.0 if workload == "create" else 150.0 if workload == "learn" else 300.0,
                "bandwidth_mbps": max(1.0, _mean(down) * 0.2),
                "origin": "inferred",
            }
        ],
        "connectivity_candidates": [
            {
                "network": "terrestrial",
                "available": terrestrial_up,
                "estimated_latency_ms": mean_latency,
                "estimated_capacity_mbps": _mean(down),
                "origin": "measured",
            },
            {
                "network": "local_edge_wifi",
                "available": local_edge_available and dominant in {"wifi", "degraded_local"},
                "estimated_latency_ms": _mean([float(m["local_edge_response_ms"]) for m in observations]),
                "estimated_capacity_mbps": _mean(down) * 0.8,
                "origin": "measured",
            },
            {
                "network": "degraded_local",
                "available": True,
                "estimated_latency_ms": mean_latency * 1.5,
                "estimated_capacity_mbps": max(0.5, _mean(down) * 0.3),
                "origin": "inferred",
            },
            {
                "network": "ntn_fallback",
                "available": True,
                "estimated_latency_ms": 45.0,
                "estimated_capacity_mbps": 5.0,
                "origin": "configured",
            },
            {
                "network": "device_to_device",
                "available": False,
                "estimated_latency_ms": None,
                "estimated_capacity_mbps": None,
                "origin": "missing",
            },
            {
                "network": "offline_continuation",
                "available": True,
                "estimated_latency_ms": 0.0,
                "estimated_capacity_mbps": 0.0,
                "origin": "configured",
            },
        ],
        "network_state": {
            "values": {
                "dominant_network_type": dominant,
                "mean_latency_ms": mean_latency,
                "mean_packet_loss_pct": _mean(loss),
                "mean_jitter_ms": _mean(jit),
            },
            "origin": "measured",
        },
        "spectrum_availability": {
            "values": {"spectrum_budget_mhz": 20.0},
            "origin": "configured",
        },
        "compute_availability": {
            "values": {
                "local_edge": local_edge_available,
                "cloud": True,
                "device": True,
                "compute_nodes": [
                    {"id": "device", "capacity": 1.0},
                    {"id": "local_edge", "capacity": 1.0 if local_edge_available else 0.0},
                    {"id": "cloud", "capacity": 1.0},
                ],
            },
            "origin": "inferred",
        },
        "mobility_state": {
            "values": {"class": "low_mobility_named_zone"},
            "origin": "configured",
        },
        "blockage_state": {
            "values": {"blocked": False},
            "origin": "missing",
        },
        "energy_constraints": {
            "values": {
                "energy_budget_j": 100.0,
                "mean_battery_pct": _mean([float(m["battery_pct"]) for m in observations]),
            },
            "origin": "measured",
        },
        "outage_state": {
            "values": {
                "terrestrial_outage": not terrestrial_up,
                "degraded": _mean(loss) > 5 or mean_latency > 120,
            },
            "origin": "inferred",
        },
        "privacy_constraints": {
            "values": {
                "location_precision": adapter.document["privacy"]["location_precision"],
                "contains_direct_identifiers": False,
                "retention_days": adapter.document["privacy"]["retention_days"],
            },
            "origin": "measured",
        },
        "continuity_requirements": {
            "values": {
                "class": "degraded_ok" if workload != "create" else "strict",
                "max_interruption_s": 30 if workload == "create" else 120,
            },
            "origin": "inferred",
        },
        "uncertainty": {
            "overall": "medium" if adapter.document["evidence_level"] == "synthetic" else "low",
            "notes": "Derived from Edge-IO batch; configured NTN parameters are not measured.",
        },
        "missing_data_flags": [
            "device_to_device_availability",
            "blockage_state",
        ],
        "field_provenance": {
            "fields": {
                "network_state": "measured",
                "service_demand": "inferred",
                "spectrum_availability": "configured",
                "ntn_fallback_latency": "configured",
                "blockage_state": "missing",
                "device_to_device": "missing",
            }
        },
        "scenario_provenance": {
            "transformer": cfg["transformer"],
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "notes": "Aggregated without modifying the source Edge-IO file.",
        },
        "configuration_hash": configuration_hash,
        "evidence_level": adapter.document["evidence_level"],
        "producer": {
            "repository": "7gc-digital-twin",
            "commit": git_commit(),
        },
        "n_users": 4,
        "service_profile": service,
        "measurement_quality": {
            "flags": sorted(
                {
                    flag
                    for m in observations
                    for flag in (m.get("quality_flags") or [])
                }
            )
        },
    }
    return twin


def ingest_edge(
    input_path: Path,
    *,
    site_id: str,
    run_id: str,
    schema_dir: Path | None = None,
    store_dir: Path | None = None,
) -> EdgeIOAdapter:
    adapter = EdgeIOAdapter(input_path, schema_dir=schema_dir)
    adapter.load()
    adapter.validate()
    adapter.verify_ids(run_id, site_id)
    if store_dir is not None:
        store_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "run_id": run_id,
            "site_id": site_id,
            "input_path": str(input_path),
            "sha256": adapter.input_sha256,
        }
        write_json(store_dir / f"{run_id}.ingest.json", meta)
    return adapter


def validate_twin_state(path: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    schema_path = resolve_schema_dir(schema_dir)
    mod = load_validator(schema_path)
    doc = load_json(path)
    return mod.validate_document(
        doc,
        schema_path,
        expected_schema_name="gunnchos.twin_state_bundle",
        enforce_privacy=False,
    )
