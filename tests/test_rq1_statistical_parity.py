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
from seven_gc_twin.stats import (
    CI_SIM_VARIABILITY_WARNING,
    MIN_SAMPLE_N,
    T_CRIT_975,
    T_CRIT_VERIFICATION_SOURCE,
    mean_ci,
    paired_diff_ci,
    t_crit_975,
)


# Predeclared frozen seed list (protocol); n=30 before outcome inspection.
FIXED_SEEDS = list(range(1, 31))

# Trusted reference: SciPy 1.18.0 scipy.stats.t.ppf(0.975, df)
SCIPY_T_PPF_975_REFERENCE = {
    1: 12.7062047362,
    3: 3.1824463053,
    11: 2.2009851601,
    19: 2.0930240544,
    29: 2.0452296421,
}


def test_t_crit_matches_scipy_reference_for_required_dfs():
    for df, expected in SCIPY_T_PPF_975_REFERENCE.items():
        assert abs(t_crit_975(df) - expected) < 1e-9
    # Large df: Cornish–Fisher must approach Φ^{-1}(0.975), not jump to bare 1.96 for missing finite df.
    assert abs(t_crit_975(1_000_000) - 1.95996398454) < 1e-4
    assert 11 in T_CRIT_975 and 19 in T_CRIT_975 and 29 in T_CRIT_975
    assert "SciPy" in T_CRIT_VERIFICATION_SOURCE


def test_t_crit_rejects_nonpositive_df():
    with pytest.raises(ValueError):
        t_crit_975(0)


def test_mean_ci_rejects_non_95_level():
    with pytest.raises(ValueError, match="0.95"):
        mean_ci([1.0, 2.0, 3.0], level=0.90)


def test_mean_ci_n_lt_2_no_degenerate_ci():
    stats = mean_ci([3.14])
    assert stats["n"] == 1
    assert math.isnan(stats["ci_low"]) and math.isnan(stats["ci_high"])


def test_mean_ci_math_known_values():
    stats = mean_ci([1.0, 2.0, 3.0, 4.0])
    assert stats["n"] == 4
    assert abs(stats["mean"] - 2.5) < 1e-12
    assert abs(stats["std"] - math.sqrt(5.0 / 3.0)) < 1e-12
    # df=3 → t_crit ≈ 3.182; half-width = t * s / sqrt(n)
    half = t_crit_975(3) * stats["std"] / 2.0
    assert abs(stats["ci_low"] - (2.5 - half)) < 1e-12
    assert abs(stats["ci_high"] - (2.5 + half)) < 1e-12


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
    assert report["n_seeds"] == 30
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


def test_paired_diff_uses_dz_not_pooled_cohens_d():
    # Exact integer paired offset → sd(diffs)=0 → d_z defined as 0.0
    paired_const = paired_diff_ci([2.0, 3.0, 4.0], [1.0, 2.0, 3.0])
    assert paired_const["paired"] is True
    assert abs(paired_const["mean"] - 1.0) < 1e-12
    assert paired_const["paired_cohens_d_z"] == 0.0
    assert "cohens_d_vs_baseline" not in paired_const
    assert "pairwise_differences" in paired_const["effect_size_definition"]

    base = [simulate_seed_continuity(s) for s in FIXED_SEEDS[:4]]
    t = [r["primary"]["task_completion_ratio"] + 0.05 for r in base]
    b = [r["primary"]["task_completion_ratio"] for r in base]
    paired = paired_diff_ci(t, b)
    assert abs(paired["mean"] - 0.05) < 1e-9
    assert math.isfinite(paired["ci_low"])
    assert "paired_cohens_d_z" in paired


def test_experiment_includes_statistical_report(tmp_path, monkeypatch):
    from seven_gc_twin.experiment_manifest import run_experiment

    monkeypatch.chdir(tmp_path)
    result = run_experiment("rq1_gary_flagship_profiles", out_dir=tmp_path)
    assert result["evidence_class"] == EVIDENCE_CLASS
    assert "statistical_report" in result
    assert result["statistical_report"]["primary"]["task_completion_ratio"]["n"] == 30
    assert result["statistical_artifacts"]["md"]
