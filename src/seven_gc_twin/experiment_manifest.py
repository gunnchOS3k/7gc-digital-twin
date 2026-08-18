"""RQ1 experiment manifests — profiles and synthetic benchmarks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .campus_metrics import compute_campus_metrics
from .config.schema import REQUIRED_EXPERIMENT_FIELDS
from .provenance import sha256_json, stamp
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
        metrics = compute_campus_metrics(site_id, mode=mode)
        scenario = run_scenario(site_id, scenario_id, mode=mode)
        runs.append(
            {
                "seed": seed,
                "scenario_id": scenario_id,
                "campus_metrics": metrics,
                "scenario": {
                    "evidence_status": scenario.get("evidence_status"),
                    "mode": scenario.get("mode"),
                },
            }
        )
    result = {
        "experiment_id": experiment_id,
        "research_question": manifest["research_question"],
        "site_id": site_id,
        "is_flagship": site_id == "gary",
        "scenario_environment_not_community_deployment": True,
        "mode": mode,
        "seeds": seeds,
        "metrics_requested": manifest["metrics"],
        "non_claims": manifest["non_claims"],
        "runs": runs,
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
    result["wrote"] = str(path)
    return result
