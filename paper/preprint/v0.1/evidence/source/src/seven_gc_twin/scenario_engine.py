"""Run campus scenarios and aggregate metrics."""
from __future__ import annotations

from .bad_day_scenarios import run_bad_day
from .campus_metrics import compute_campus_metrics
from .community_benefit import community_benefit_report
from .local_capacity import local_capacity_plan
from .site_profiles import list_profile_sites


def run_scenario(site_id: str, scenario_id: str, mode: str = "smoke") -> dict:
    metrics = compute_campus_metrics(site_id, mode=mode)
    bad = run_bad_day(site_id, scenario_id, mode=mode) if scenario_id else {}
    return {
        "site_id": site_id,
        "scenario_id": scenario_id,
        "mode": mode,
        "campus_metrics": metrics,
        "bad_day": bad,
        "community_benefit": community_benefit_report(site_id, metrics),
        "local_capacity": local_capacity_plan(site_id),
        "evidence_status": "smoke_test_only",
    }


def run_all_sites(mode: str = "smoke") -> list[dict]:
    from .site_profiles import load_profile

    out = []
    for sid in list_profile_sites():
        profile = load_profile(sid)
        first_bad = profile["bad_day_scenarios"][0]["scenario_id"]
        out.append(run_scenario(sid, first_bad, mode=mode))
    return out
