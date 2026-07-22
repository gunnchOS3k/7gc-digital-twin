"""7GC Gate 2 ingestion tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from seven_gc_twin.gate2.common import sha256_file
from seven_gc_twin.gate2.edge_ingest import EdgeIOAdapter, build_twin_state, validate_twin_state

FK = Path(__file__).resolve().parents[3] / "gunnchos-7gc-ai-ran-field-kit"
SCHEMA = FK / "contracts"
EDGE = FK / "fixtures/valid/edge_measurement_batch.valid.json"


def test_invalid_edge_fails_before_build(tmp_path):
    doc = json.loads(EDGE.read_text())
    doc["measurements"][0]["latency_ms"] = -1
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(doc))
    adapter = EdgeIOAdapter(bad, schema_dir=SCHEMA)
    adapter.load()
    with pytest.raises(Exception):
        adapter.validate()


def test_valid_batch_builds_without_manual_edit(tmp_path):
    adapter = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    adapter.load()
    twin = build_twin_state(adapter, run_id=adapter.document["run_id"], site_id=adapter.document["site_id"])
    out = tmp_path / "twin.json"
    out.write_text(json.dumps(twin, indent=2))
    validate_twin_state(out, schema_dir=SCHEMA)
    assert twin["source_measurement"]["sha256"] == sha256_file(EDGE)


def test_hash_changes_when_source_changes(tmp_path):
    adapter = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    adapter.load()
    t1 = build_twin_state(adapter, run_id=adapter.document["run_id"], site_id=adapter.document["site_id"])
    doc = json.loads(EDGE.read_text())
    doc["measurements"][0]["latency_ms"] = float(doc["measurements"][0]["latency_ms"]) + 1.0
    alt = tmp_path / "alt.json"
    alt.write_text(json.dumps(doc))
    adapter2 = EdgeIOAdapter(alt, schema_dir=SCHEMA)
    adapter2.load()
    t2 = build_twin_state(adapter2, run_id=adapter2.document["run_id"], site_id=adapter2.document["site_id"])
    assert t1["source_measurement"]["sha256"] != t2["source_measurement"]["sha256"]


def test_reproducible_for_identical_input():
    a1 = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    a1.load()
    t1 = build_twin_state(a1, run_id=a1.document["run_id"], site_id=a1.document["site_id"])
    a2 = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    a2.load()
    t2 = build_twin_state(a2, run_id=a2.document["run_id"], site_id=a2.document["site_id"])
    # configuration hash and source hash stable; generated_at may differ — compare core fields
    assert t1["configuration_hash"] == t2["configuration_hash"]
    assert t1["source_measurement"] == t2["source_measurement"]
    assert t1["network_state"] == t2["network_state"]


def test_origins_distinguishable():
    adapter = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    adapter.load()
    twin = build_twin_state(adapter, run_id=adapter.document["run_id"], site_id=adapter.document["site_id"])
    origins = {twin["network_state"]["origin"], twin["spectrum_availability"]["origin"], twin["service_demand"]["origin"]}
    assert "measured" in origins
    assert "configured" in origins
    assert "inferred" in origins
    assert "missing" in twin["field_provenance"]["fields"].values() or twin["missing_data_flags"]


def test_null_unavailable_metrics_do_not_crash_build(tmp_path):
    doc = json.loads(EDGE.read_text())
    for m in doc["measurements"]:
        m["jitter_ms"] = None
        m["upload_mbps"] = None
        m["download_mbps"] = None
        m["packet_loss_pct"] = None
        m["unavailable_fields"] = {
            "jitter_ms": "api_not_exposed_without_privileged_radio_stats",
            "upload_mbps": "api_not_exposed_without_privileged_radio_stats",
            "download_mbps": "api_not_exposed_without_privileged_radio_stats",
            "packet_loss_pct": "api_not_exposed_without_privileged_radio_stats",
        }
    path = tmp_path / "physical_nulls.json"
    path.write_text(json.dumps(doc))
    adapter = EdgeIOAdapter(path, schema_dir=SCHEMA)
    adapter.load()
    twin = build_twin_state(adapter, run_id=doc["run_id"], site_id=doc["site_id"])
    assert twin["source_measurement"]["summary"]["n_samples"] == len(doc["measurements"])
    assert twin["source_measurement"]["summary"]["mean_latency_ms"] >= 0

    adapter = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    adapter.load()
    # Strip path operates on already-loaded documents before twin export.
    adapter.document.setdefault("annotations", {})["email"] = "x@y.z"
    cleaned_obs = adapter.to_twin_observations()
    assert "email" not in json.dumps(cleaned_obs)
    from seven_gc_twin.gate2.edge_ingest import _strip_prohibited

    stripped = _strip_prohibited(adapter.document)
    assert "email" not in json.dumps(stripped)
    # Rebuild from clean source for a schema-valid twin export.
    clean = EdgeIOAdapter(EDGE, schema_dir=SCHEMA)
    clean.load()
    twin = build_twin_state(
        clean, run_id=clean.document["run_id"], site_id=clean.document["site_id"]
    )
    assert "email" not in json.dumps(twin)
