"""RQ1 statistical parity: CI math, seeds, schema, evidence labeling."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from seven_gc_twin.rq1_statistical_report import (
    EVIDENCE_CLASS,
    SCENARIO_FAMILY_ID,
    build_statistical_report,
    simulate_seed_continuity,
    write_statistical_artifacts,
)
from seven_gc_twin.stats import CI_SIM_VARIABILITY_WARNING, MIN_SAMPLE_N, mean_ci, paired_diff_ci


FIXED_SEEDS = [1, 2, 7, 42]


def test_mean_ci_math_known_values():
    stats = mean_ci([1.0, 2.0, 3.0, 4.0])
    assert stats["n"] == 4
    assert abs(stats["mean"] - 2.5) < 1e-12
    assert abs(stats["std"] - math.sqrt(5.0 / 3.0)) < 1e-12
    assert stats["ci_low"] < stats["mean"] < stats["ci_high"]


def test_fixed_seed_reproducibility():
    a = simulate_seed_continuity(7)
    b = simulate_seed_continuity(7)
    c = simulate_seed_continuity(8)
    assert a["primary"] == b["primary"]
    assert a["primary"] != c["primary"]
    assert a["evidence_class"] == EVIDENCE_CLASS


def test_statistical_report_schema_and_no_nan(tmp_path):
    report = build_statistical_report(FIXED_SEEDS)
    assert report["n_seeds"] >= MIN_SAMPLE_N
    assert report["seeds"] == FIXED_SEEDS
    assert report["scenario_family_id"] == SCENARIO_FAMILY_ID
    assert report["evidence_class"] == EVIDENCE_CLASS
    assert report["ci_warning"] == CI_SIM_VARIABILITY_WARNING
    assert report["no_composite_metric"] is True
    for metric, stats in report["primary"].items():
        for key in ("n", "mean", "std", "ci_low", "ci_high"):
            assert key in stats, metric
            assert math.isfinite(stats[key])
    paths = write_statistical_artifacts(report, tmp_path)
    assert Path(paths["json"]).exists()
    assert Path(paths["csv"]).exists()
    assert Path(paths["md"]).exists()
    md = Path(paths["md"]).read_text(encoding="utf-8")
    assert "SYNTHETIC_SIM" in md
    assert "NOT real-world RF" in md


def test_min_sample_count_enforced():
    with pytest.raises(ValueError):
        build_statistical_report([42])


def test_paired_diff_when_seed_matched():
    base = [simulate_seed_continuity(s) for s in FIXED_SEEDS]
    # Shifted "treatment": reuse same seeds but compare to a constant offset series via paired helper
    t = [r["primary"]["task_completion_ratio"] + 0.05 for r in base]
    b = [r["primary"]["task_completion_ratio"] for r in base]
    paired = paired_diff_ci(t, b)
    assert paired["paired"] is True
    assert abs(paired["mean"] - 0.05) < 1e-9
    assert math.isfinite(paired["ci_low"])


def test_experiment_includes_statistical_report(tmp_path, monkeypatch):
    from seven_gc_twin.experiment_manifest import run_experiment

    monkeypatch.chdir(tmp_path)
    result = run_experiment("rq1_gary_flagship_profiles", out_dir=tmp_path)
    assert result["evidence_class"] == EVIDENCE_CLASS
    assert "statistical_report" in result
    assert result["statistical_report"]["primary"]["task_completion_ratio"]["n"] == 4
    assert result["statistical_artifacts"]["md"]
