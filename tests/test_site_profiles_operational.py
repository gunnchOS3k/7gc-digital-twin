"""Tests for grounded campus site profiles."""
from pathlib import Path

import pytest

from seven_gc_twin.campus_reports import write_site_bundle
from seven_gc_twin.integrations import integration_map
from seven_gc_twin.scenario_engine import run_all_sites, run_scenario
from seven_gc_twin.site_profiles import list_profile_sites, load_profile, validate_all_profiles
from seven_gc_twin.use_cases import list_use_cases, repos_for_site


def test_all_profiles_load():
    assert validate_all_profiles() == []
    assert len(list_profile_sites()) == 7


@pytest.mark.parametrize("site_id", list_profile_sites())
def test_profile_requirements(site_id: str):
    p = load_profile(site_id)
    assert len(p["anchor_use_cases"]) >= 3
    assert len(p["resilience_use_cases"]) >= 2
    assert len(p["bad_day_scenarios"]) >= 5
    assert len(p["no_foreign_savior_guardrails"]) >= 5
    assert len(p["evidence_to_collect"]) >= 5
    for uc in list_use_cases(site_id):
        assert uc.get("use_case_id")
    assert repos_for_site(site_id)


def test_scenario_engine_smoke():
    sid = list_profile_sites()[0]
    p = load_profile(sid)
    sc = p["bad_day_scenarios"][0]["scenario_id"]
    r = run_scenario(sid, sc, mode="smoke")
    assert r["evidence_status"] == "smoke_test_only"


def test_run_all_sites():
    results = run_all_sites(mode="smoke")
    assert len(results) == 7


def test_write_bundle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bundle = write_site_bundle("gary", mode="smoke")
    assert Path(bundle["paths"]["profile_json"]).exists()


def test_integration_map():
    m = integration_map("ghana")
    assert "edge_io" in m
