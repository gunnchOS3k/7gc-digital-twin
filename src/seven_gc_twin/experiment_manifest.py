"""RQ1 experiment manifests — profiles and synthetic benchmarks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .campus_metrics import compute_campus_metrics
from .config.schema import REQUIRED_EXPERIMENT_FIELDS
from .continuity_benchmark import analyze_continuity, site_metric_panel
from .provenance import sha256_json, stamp
from .rq1_statistical_report import (
    SCENARIO_FAMILY_ID,
    build_statistical_report,
    write_statistical_artifacts,
)
from .scenario_engine import run_scenario
from .site_profiles import load_profile

EXPERIMENTS_DIR = Path(__file__).resolve().parents[2] / "configs" / "experiments"


def list_experiments() -> list[str]:
    return sorted(p.stem for p in EXPERIMENTS_DIR.glob("*.yaml"))


def load_manifest(experiment_id: str) -> dict[str, Any]:
    path = EXPERIMENTS_DIR / f"{experiment_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Unknown experiment: {experiment_id}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("experiment_id") != experiment_id:
        raise ValueError(f"experiment_id mismatch in {path}")
    missing = [k for k in REQUIRED_EXPERIMENT_FIELDS if k not in data]
    if missing:
        raise ValueError(f"Missing experiment fields {missing} in {path}")
    return data


def run_experiment(experiment_id: str, out_dir: Path | None = None) -> dict[str, Any]:
    manifest = load_manifest(experiment_id)
    site_id = manifest["site_id"]
    mode = manifest.get("mode", "synthetic-fixture")
    profile = load_profile(site_id)
    scenario_id = manifest.get("scenario_id") or profile["bad_day_scenarios"][0]["scenario_id"]
    seeds = list(manifest.get("seeds") or [42])
    runs = []
    for seed in seeds:
        metrics = compute_campus_metrics(site_id, mode=mode, seed=seed)
        scenario = run_scenario(site_id, scenario_id, mode=mode)
        wl = metrics["families"]["workload"]
        radio = metrics["families"]["radio"]
        runs.append(
            {
                "seed": seed,
                "scenario_id": scenario_id,
                "mean_demand_mbps": wl["mean_demand_mbps"],
                "p95_demand_mbps": wl["p95_demand_mbps"],
                "jains_fairness_on_demand": wl["jains_fairness_on_demand"],
                "radio_evidence_status": radio["evidence_status"],
                "sinr_db_stub": radio["sinr_db_stub"],
                "campus_metrics": metrics,
                "scenario": {
                    "evidence_status": scenario.get("evidence_status"),
                    "mode": scenario.get("mode"),
                },
            }
        )
    mapping = manifest.get("gary_scenario_to_bearer_stress")
    continuity = analyze_continuity(mapping=mapping, site_id=site_id)
    panel = site_metric_panel(seeds, mode=mode)
    scenario_family_id = manifest.get("scenario_family_id") or SCENARIO_FAMILY_ID
    statistical_report = build_statistical_report(seeds, scenario_family_id=scenario_family_id)
    result = {
        "experiment_id": experiment_id,
        "research_question": manifest["research_question"],
        "site_id": site_id,
        "is_flagship": site_id == "gary",
        "scenario_environment_not_community_deployment": True,
        "mode": mode,
        "seeds": seeds,
        "scenario_family_id": scenario_family_id,
        "evidence_class": "SYNTHETIC_SIM",
        "metrics_requested": manifest["metrics"],
        "non_claims": manifest["non_claims"],
        "runs": runs,
        "continuity_benchmark": continuity,
        "site_metric_panel": panel,
        "statistical_report": statistical_report,
        "findings": {
            "classes_that_failed": continuity["classes_that_failed"],
            "classes_never_failed": continuity["classes_never_failed"],
            "n_failed_cases": len(continuity["failed_cases"]),
            "n_min_useful_cases": len(continuity["min_useful_cases"]),
            "degraded_wifi_n_still_target": len(continuity["degraded_wifi_still_target"]),
            "gary_overlay_n_below_min_useful": len(continuity["gary_overlay_below_min_useful"]),
            "gary_mean_demand_mbps_min": panel["gary_mean_demand_mbps_min"],
            "gary_mean_demand_mbps_max": panel["gary_mean_demand_mbps_max"],
            "gary_mean_demand_mbps_range": panel["gary_mean_demand_mbps_range"],
            "level_rederive_all_match": continuity["level_rederive_all_match"],
            "digest_match": continuity["digest_match"],
            "primary_task_completion_mean": statistical_report["primary"]["task_completion_ratio"][
                "mean"
            ],
            "primary_time_above_min_useful_mean": statistical_report["primary"][
                "time_above_minimum_useful"
            ]["mean"],
        },
        "provenance": stamp(
            artifact_kind="rq1_experiment",
            site_id=site_id,
            mode=mode,
            extra={"experiment_id": experiment_id, "n_seeds": len(seeds)},
        ),
    }
    result["result_sha256"] = sha256_json(result)
    dest = out_dir or Path("results/experiments")
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{experiment_id}.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    stats_paths = write_statistical_artifacts(statistical_report, dest)
    result["wrote"] = str(path)
    result["statistical_artifacts"] = stats_paths
    return result
