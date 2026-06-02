"""Bad-day scenario helpers."""
from __future__ import annotations

from .site_profiles import load_profile


def list_bad_days(site_id: str) -> list[dict]:
    return load_profile(site_id)["bad_day_scenarios"]


def run_bad_day(site_id: str, scenario_id: str, mode: str = "smoke") -> dict:
    scenarios = {s["scenario_id"]: s for s in list_bad_days(site_id)}
    if scenario_id not in scenarios:
        raise KeyError(f"Unknown bad-day scenario {scenario_id} for {site_id}")
    base = scenarios[scenario_id]
    return {
        "site_id": site_id,
        "scenario_id": scenario_id,
        "mode": mode,
        "evidence_status": "smoke_test_only" if mode == "smoke" else "research_run",
        "description": base.get("description"),
        "metrics": base.get("metrics", []),
        "stress_score": 0.55 if mode == "smoke" else 0.5,
        "needs_local_validation": True,
        "note": "Synthetic scenario metrics — not field validation",
    }
