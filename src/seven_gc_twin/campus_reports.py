"""Generate campus operational report artifacts."""
from __future__ import annotations

import json
from pathlib import Path

from .campus_metrics import compute_campus_metrics
from .community_benefit import community_benefit_report
from .local_capacity import local_capacity_plan
from .scenario_engine import run_scenario
from .site_profiles import load_profile, list_profile_sites
from .use_cases import list_use_cases, repos_for_site

OUT = Path("results/site_profiles")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_site_bundle(site_id: str, mode: str = "smoke") -> dict:
    profile = load_profile(site_id)
    metrics = compute_campus_metrics(site_id, mode=mode)
    scenario_id = profile["bad_day_scenarios"][0]["scenario_id"]
    run = run_scenario(site_id, scenario_id, mode=mode)
    paths = {}
    paths["profile_json"] = _write(OUT / f"{site_id}_profile.json", json.dumps(profile, indent=2))
    ucs = list_use_cases(site_id)
    uc_md = "\n".join(f"- **{u['use_case_id']}** ({u['kind']}): {u['name']}" for u in ucs)
    paths["use_cases"] = _write(OUT / f"{site_id}_use_case_register.md", f"# Use cases — {site_id}\n\n{uc_md}\n")
    bad_md = "\n".join(f"- `{b['scenario_id']}`: {b['description']}" for b in profile["bad_day_scenarios"])
    paths["bad_days"] = _write(OUT / f"{site_id}_bad_day_scenarios.md", f"# Bad days — {site_id}\n\n{bad_md}\n")
    cb = community_benefit_report(site_id, metrics)
    paths["benefit"] = _write(
        OUT / f"{site_id}_community_benefit_report.md",
        f"# Community benefit — {site_id}\n\nEvidence: **{cb['evidence_status']}**\n\n```json\n{json.dumps(cb, indent=2)}\n```\n",
    )
    lc = local_capacity_plan(site_id)
    paths["capacity"] = _write(
        OUT / f"{site_id}_local_capacity_plan.md",
        f"# Local capacity — {site_id}\n\n```json\n{json.dumps(lc, indent=2)}\n```\n",
    )
    paths["metrics_json"] = _write(OUT / f"{site_id}_scenario_metrics.json", json.dumps(run, indent=2))
    table = (
        f"| Metric | Value |\n|--------|-------|\n"
        + "\n".join(f"| {k} | {v} |" for k, v in metrics.items() if k not in ("site_id", "mode"))
    )
    paths["conference"] = _write(
        OUT / f"{site_id}_conference_table.md",
        f"# Conference table — {site_id}\n\n**Status:** smoke test only — needs local validation\n\n{table}\n",
    )
    return {"site_id": site_id, "paths": {k: str(v) for k, v in paths.items()}, "repos": sorted(repos_for_site(site_id))}


def write_all_sites(mode: str = "smoke") -> list[dict]:
    return [write_site_bundle(s, mode=mode) for s in list_profile_sites()]
