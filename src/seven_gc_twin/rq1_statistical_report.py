"""RQ1 seeded statistical reporting path (SYNTHETIC_SIM).

Primary outcomes (V3-aligned, no composite that hides components):
  - task_completion_ratio
  - time_above_minimum_useful

Secondary outcomes are reported separately. Seeded timelines jitter demand and
outage around frozen Device OS continuity class behaviors.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from .continuity_benchmark import LEVEL_ORDER, analyze_continuity, classify_continuity, load_profiles
from .stats import (
    CI_SIM_VARIABILITY_WARNING,
    MIN_SAMPLE_N,
    assert_finite,
    cohens_d,
    mean_ci,
    paired_diff_ci,
    schema_keys,
)

SCENARIO_FAMILY_ID = "gary_flagship_continuity_profiles"
EVIDENCE_CLASS = "SYNTHETIC_SIM"
DEFAULT_STEPS = 48
RESEARCH_CLASSES = ("wearable", "smartphone", "laptop", "edge_node")

# Class base resilience under seeded stress (documented synthetic priors).
CLASS_BASE = {
    "wearable": {"task_base": 0.55, "min_useful_base": 0.45, "stress_sens": 1.35},
    "smartphone": {"task_base": 0.78, "min_useful_base": 0.72, "stress_sens": 1.0},
    "laptop": {"task_base": 0.85, "min_useful_base": 0.80, "stress_sens": 0.85},
    "edge_node": {"task_base": 0.90, "min_useful_base": 0.88, "stress_sens": 0.70},
}


def simulate_seed_continuity(
    seed: int,
    *,
    steps: int = DEFAULT_STEPS,
    scenario_family_id: str = SCENARIO_FAMILY_ID,
) -> dict[str, Any]:
    """Per-seed synthetic continuity timeline for primary outcomes."""
    rng = random.Random(seed)
    class_rows: dict[str, dict[str, Any]] = {}
    for cls in RESEARCH_CLASSES:
        prior = CLASS_BASE[cls]
        above = 0
        completed = 0
        outage_steps = 0
        recovery_events = 0
        qoe_violations = 0
        energy_proxy = 0.0
        latencies: list[float] = []
        in_outage = False
        for _ in range(steps):
            stress = rng.random()
            demand = 1.0 + 49.0 * rng.random()
            meets_min = rng.random() < prior["min_useful_base"] * (
                1.0 - prior["stress_sens"] * 0.35 * stress
            )
            task_ok = meets_min and (rng.random() < prior["task_base"] * (1.0 - 0.2 * stress))
            if not meets_min:
                outage_steps += 1
                qoe_violations += 1
                if not in_outage:
                    recovery_events += 1
                in_outage = True
            else:
                in_outage = False
                above += 1
            if task_ok:
                completed += 1
            energy_proxy += 0.02 * demand * (1.2 if meets_min else 0.6)
            latencies.append(20.0 + 180.0 * stress * prior["stress_sens"])
        time_above = above / max(steps, 1)
        task_ratio = completed / max(steps, 1)
        assert_finite([time_above, task_ratio], label=f"{cls}:{seed}")
        class_rows[cls] = {
            "task_completion_ratio": round(task_ratio, 6),
            "time_above_minimum_useful": round(time_above, 6),
            "outage_fraction": round(outage_steps / max(steps, 1), 6),
            "recovery_event_count": recovery_events,
            "qoe_violation_fraction": round(qoe_violations / max(steps, 1), 6),
            "energy_proxy_j": round(energy_proxy, 4),
            "mean_latency_ms": round(sum(latencies) / max(len(latencies), 1), 4),
            "mean_jitter_ms": round(
                sum(abs(latencies[i] - latencies[i - 1]) for i in range(1, len(latencies)))
                / max(len(latencies) - 1, 1),
                4,
            )
            if len(latencies) > 1
            else 0.0,
            "packet_loss_proxy": round(1.0 - time_above, 6),
            "throughput_proxy_mbps": round(time_above * 5.0, 4),
            "reliability": round(time_above, 6),
            "compute_completion_time_proxy": round(steps * (1.2 - 0.4 * task_ratio), 4),
        }
    task_vals = [class_rows[c]["task_completion_ratio"] for c in RESEARCH_CLASSES]
    tau_vals = [class_rows[c]["time_above_minimum_useful"] for c in RESEARCH_CLASSES]
    return {
        "seed": seed,
        "scenario_family_id": scenario_family_id,
        "steps": steps,
        "per_class": class_rows,
        "primary": {
            "task_completion_ratio": round(sum(task_vals) / len(task_vals), 6),
            "time_above_minimum_useful": round(sum(tau_vals) / len(tau_vals), 6),
        },
        "evidence_class": EVIDENCE_CLASS,
    }


def build_statistical_report(
    seeds: list[int],
    *,
    steps: int = DEFAULT_STEPS,
    scenario_family_id: str = SCENARIO_FAMILY_ID,
    baseline_seed_outcomes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if len(seeds) < MIN_SAMPLE_N:
        raise ValueError(f"Need at least {MIN_SAMPLE_N} seeds for Student-t CI; got {len(seeds)}")
    per_seed = [
        simulate_seed_continuity(s, steps=steps, scenario_family_id=scenario_family_id) for s in seeds
    ]
    task_series = [r["primary"]["task_completion_ratio"] for r in per_seed]
    tau_series = [r["primary"]["time_above_minimum_useful"] for r in per_seed]
    assert_finite(task_series + tau_series)

    primary = {
        "task_completion_ratio": mean_ci(task_series),
        "time_above_minimum_useful": mean_ci(tau_series),
    }
    secondary_keys = [
        "outage_fraction",
        "qoe_violation_fraction",
        "energy_proxy_j",
        "mean_latency_ms",
        "mean_jitter_ms",
        "packet_loss_proxy",
        "throughput_proxy_mbps",
        "reliability",
        "compute_completion_time_proxy",
    ]
    secondary: dict[str, Any] = {}
    for key in secondary_keys:
        series = []
        for r in per_seed:
            vals = [r["per_class"][c][key] for c in RESEARCH_CLASSES]
            series.append(sum(vals) / len(vals))
        secondary[key] = mean_ci(series)

    per_class_stats: dict[str, Any] = {}
    for cls in RESEARCH_CLASSES:
        per_class_stats[cls] = {
            "task_completion_ratio": mean_ci(
                [r["per_class"][cls]["task_completion_ratio"] for r in per_seed]
            ),
            "time_above_minimum_useful": mean_ci(
                [r["per_class"][cls]["time_above_minimum_useful"] for r in per_seed]
            ),
        }

    paired = None
    effect = None
    if baseline_seed_outcomes is not None:
        b_task = [r["primary"]["task_completion_ratio"] for r in baseline_seed_outcomes]
        b_tau = [r["primary"]["time_above_minimum_useful"] for r in baseline_seed_outcomes]
        paired = {
            "task_completion_ratio": paired_diff_ci(task_series, b_task),
            "time_above_minimum_useful": paired_diff_ci(tau_series, b_tau),
        }
        effect = {
            "task_completion_ratio_cohens_d": cohens_d(task_series, b_task),
            "time_above_minimum_useful_cohens_d": cohens_d(tau_series, b_tau),
        }

    corpus = analyze_continuity()
    return {
        "scenario_family_id": scenario_family_id,
        "seeds": list(seeds),
        "n_seeds": len(seeds),
        "steps_per_seed": steps,
        "evidence_class": EVIDENCE_CLASS,
        "ci_method": "student_t_over_seed_means",
        "ci_level": 0.95,
        "ci_warning": CI_SIM_VARIABILITY_WARNING,
        "primary_outcomes": ["task_completion_ratio", "time_above_minimum_useful"],
        "no_composite_metric": True,
        "per_seed": per_seed,
        "primary": primary,
        "secondary": secondary,
        "per_class": per_class_stats,
        "paired_vs_baseline": paired,
        "effect_sizes": effect,
        "schema": {"mean_ci_keys": schema_keys()},
        "frozen_corpus_classes_that_failed": corpus.get("classes_that_failed"),
        "level_order_reference": LEVEL_ORDER,
        "classify_rule_probe": {
            "connected": classify_continuity("connected", offline_covers_workload=False),
            "offline_covers": classify_continuity("offline", offline_covers_workload=True),
        },
        "profile_bundle_present": bool(load_profiles().get("profiles")),
    }


def write_statistical_artifacts(report: dict[str, Any], dest: Path) -> dict[str, str]:
    dest.mkdir(parents=True, exist_ok=True)
    json_path = dest / "rq1_statistical_report.json"
    csv_path = dest / "rq1_statistical_report.csv"
    md_path = dest / "rq1_statistical_report.md"

    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["metric_group", "metric", "seed_or_agg", "value", "n", "mean", "std", "ci_low", "ci_high"]
        )
        for seed_row in report["per_seed"]:
            for metric, val in seed_row["primary"].items():
                w.writerow(["primary", metric, f"seed_{seed_row['seed']}", val, "", "", "", "", ""])
        for metric, stats in report["primary"].items():
            w.writerow(
                [
                    "primary",
                    metric,
                    "aggregate",
                    "",
                    stats["n"],
                    stats["mean"],
                    stats["std"],
                    stats["ci_low"],
                    stats["ci_high"],
                ]
            )
        for metric, stats in report["secondary"].items():
            w.writerow(
                [
                    "secondary",
                    metric,
                    "aggregate",
                    "",
                    stats["n"],
                    stats["mean"],
                    stats["std"],
                    stats["ci_low"],
                    stats["ci_high"],
                ]
            )

    lines = [
        "# RQ1 statistical report (SYNTHETIC_SIM)",
        "",
        f"- scenario_family_id: `{report['scenario_family_id']}`",
        f"- seeds: `{report['seeds']}`",
        f"- n: {report['n_seeds']}",
        f"- CI method: {report['ci_method']} @ {report['ci_level']}",
        f"- evidence_class: `{report['evidence_class']}`",
        "",
        f"> {report['ci_warning']}",
        "",
        "## Primary outcomes",
        "",
        "| metric | n | mean | std | 95% CI low | 95% CI high |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric, stats in report["primary"].items():
        lines.append(
            f"| {metric} | {stats['n']} | {stats['mean']:.6f} | {stats['std']:.6f} | "
            f"{stats['ci_low']:.6f} | {stats['ci_high']:.6f} |"
        )
    lines += [
        "",
        "## Per-seed primary",
        "",
        "| seed | task_completion_ratio | time_above_minimum_useful |",
        "|---:|---:|---:|",
    ]
    for seed_row in report["per_seed"]:
        p = seed_row["primary"]
        lines.append(
            f"| {seed_row['seed']} | {p['task_completion_ratio']:.6f} | "
            f"{p['time_above_minimum_useful']:.6f} |"
        )
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "md": str(md_path)}
