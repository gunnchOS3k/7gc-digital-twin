"""RQ1 supervisor-ready digital checks: schemas, fixtures, provenance, metrics."""
from __future__ import annotations

import json
from pathlib import Path

from seven_gc_twin.campus_metrics import compute_campus_metrics
from seven_gc_twin.config.schema import (
    ALL_SITE_IDS,
    FLAGSHIP_SITE_ID,
    METRIC_FAMILIES,
    SCENARIO_ENVIRONMENT_IDS,
)
from seven_gc_twin.experiment_manifest import list_experiments, load_manifest, run_experiment
from seven_gc_twin.sites import load_site


ROOT = Path(__file__).resolve().parents[1]


def test_gary_is_flagship_and_others_are_scenario_environments():
    gary = load_site("gary")
    assert gary["is_flagship"] is True
    assert gary["node_role"] == "flagship_scenario"
    assert gary["scenario_environment_not_community_deployment"] is True
    for sid in SCENARIO_ENVIRONMENT_IDS:
        site = load_site(sid)
        assert site["is_flagship"] is False
        assert site["scenario_environment_not_community_deployment"] is True
        assert site["site_id"] in ALL_SITE_IDS
    assert FLAGSHIP_SITE_ID == "gary"


def test_metric_families_are_synthetic_not_rf():
    m = compute_campus_metrics("gary", mode="synthetic-fixture")
    for family in METRIC_FAMILIES:
        assert family in m["families"]
    assert m["families"]["radio"]["evidence_status"] == "synthetic_fixture"
    assert "not a channel sounding" in m["families"]["radio"]["note"]
    assert m["scenario_environment_not_community_deployment"] is True
    assert m["provenance"]["producer"]["repository"] == "7gc-digital-twin"
    assert "Not University of Oulu affiliation" in m["provenance"]["non_claims"]


def test_synthetic_user_fixture_exists():
    path = ROOT / "fixtures/synthetic/gary_users.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["evidence_status"] == "synthetic_fixture"
    assert data["site_id"] == "gary"
    assert len(data["users"]) >= 4


def test_rq1_experiment_manifest_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert "rq1_gary_flagship_profiles" in list_experiments()
    manifest = load_manifest("rq1_gary_flagship_profiles")
    assert manifest["research_question"] == "RQ1"
    result = run_experiment("rq1_gary_flagship_profiles", out_dir=tmp_path)
    assert result["is_flagship"] is True
    assert Path(result["wrote"]).exists()
    assert len(result["runs"]) == len(manifest["seeds"])
    assert result["result_sha256"]
    assert "wearable" in result["findings"]["classes_that_failed"]
    failed = result["continuity_benchmark"]["failed_cases"]
    assert any(
        r["research_class"] == "wearable" and r["workload"] == "offline_coding" for r in failed
    )
    assert result["continuity_benchmark"]["level_rederive_all_match"] is True
    demands = {r["mean_demand_mbps"] for r in result["runs"]}
    assert len(demands) == len(result["runs"])


def test_continuity_classify_rule():
    from seven_gc_twin.continuity_benchmark import classify_continuity

    assert classify_continuity("connected", offline_covers_workload=False) == "target"
    assert classify_continuity("degraded", offline_covers_workload=True) == "degraded"
    assert classify_continuity("offline", offline_covers_workload=True) == "min_useful"
    assert classify_continuity("offline", offline_covers_workload=False) == "failed"
