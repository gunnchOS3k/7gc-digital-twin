"""Campus scenario labels stay synthetic. Mode strings cannot mint physical claims."""

import pytest

from seven_gc_twin.bad_day_scenarios import run_bad_day
from seven_gc_twin.campus_metrics import compute_campus_metrics, synthetic_evidence_status
from seven_gc_twin.scenario_engine import run_scenario
from seven_gc_twin.site_profiles import list_profile_sites, load_profile


def test_known_toy_modes_stay_smoke():
    for mode in ("smoke", "toy", "synthetic-fixture", "local-safe"):
        assert synthetic_evidence_status(mode) == "smoke_test_only"


def test_unknown_mode_is_not_echoed_as_evidence():
    assert synthetic_evidence_status("research") == "synthetic_unspecified"


@pytest.mark.parametrize("mode", ["physical", "measured_rf", "FULL_V1_RELEASED", "certified", "ota"])
def test_physical_mode_is_rejected(mode: str):
    with pytest.raises(ValueError, match="cannot adopt evidence mode"):
        synthetic_evidence_status(mode)


def test_bad_day_toy_is_not_research_run():
    site_id = list_profile_sites()[0]
    scenario_id = load_profile(site_id)["bad_day_scenarios"][0]["scenario_id"]
    result = run_bad_day(site_id, scenario_id, mode="toy")
    assert result["evidence_status"] == "smoke_test_only"
    assert result["evidence_status"] != "research_run"
    assert result["note"].startswith("Synthetic scenario metrics")


def test_scenario_engine_rejects_physical_mode():
    site_id = list_profile_sites()[0]
    scenario_id = load_profile(site_id)["bad_day_scenarios"][0]["scenario_id"]
    with pytest.raises(ValueError, match="cannot adopt evidence mode"):
        run_scenario(site_id, scenario_id, mode="physical")


def test_campus_metrics_maturity_stays_synthetic():
    metrics = compute_campus_metrics("gary", mode="synthetic-fixture")
    assert metrics["evidence_status"] == "smoke_test_only"
    assert metrics["evidence_maturity_level"] == 1
    assert metrics["families"]["radio"]["evidence_status"] == "synthetic_fixture"
