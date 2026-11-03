"""Paper I lineage: committed tables/CSVs equal a fresh regeneration, and Method/Results prose matches the data."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from seven_gc_twin.experiment_manifest import run_experiment

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
EXPERIMENT = "rq1_gary_flagship_profiles"


@pytest.fixture(scope="module")
def regen(tmp_path_factory):
    out = tmp_path_factory.mktemp("paper1")
    data = run_experiment(EXPERIMENT, out_dir=out / "results")
    spec = importlib.util.spec_from_file_location("p1_generate_tables", PAPER / "scripts" / "generate_tables.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    gen.SRC = out / "results" / f"{EXPERIMENT}.json"
    for name in ("TABLES", "FIGURES", "ARTIFACTS"):
        target = out / name.lower()
        target.mkdir()
        setattr(gen, name, target)
    gen._try_png = lambda *a, **k: None
    gen._write = lambda path, text: path.write_text(text, encoding="utf-8")
    assert gen.main() == 0
    return data, out


def _norm(p: Path) -> str:
    # The "% sha" comment hashes the provenance stamp, which changes on every run.
    lines = p.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    return "\n".join(line for line in lines if not line.startswith("% sha "))


def _section(name: str) -> str:
    return _norm(PAPER / "sections" / f"{name}.tex")


@pytest.mark.parametrize("name", sorted(p.name for p in (PAPER / "tables").glob("*.tex")))
def test_committed_table_matches_regeneration(regen, name):
    _, out = regen
    assert _norm(PAPER / "tables" / name) == _norm(out / "tables" / name), f"stale table {name}: run make paper-reproduce"


@pytest.mark.parametrize("name", sorted(p.name for p in (PAPER / "figures").glob("*.csv")))
def test_committed_figure_csv_matches_regeneration(regen, name):
    _, out = regen
    assert _norm(PAPER / "figures" / name) == _norm(out / "figures" / name), f"stale figure data {name}"


def test_prose_seeds_match_predeclared_config(regen):
    data, _ = regen
    config = yaml.safe_load((ROOT / "configs" / "experiments" / f"{EXPERIMENT}.yaml").read_text(encoding="utf-8"))
    seeds = list(config["seeds"])
    assert seeds == list(range(1, 31))
    assert [r["seed"] for r in data["runs"]] == seeds
    assert [r["seed"] for r in data["site_metric_panel"]["gary_seed_runs"]] == seeds
    assert "Seeds are $1,\\dots,30$ ($n{=}30$" in _section("method")
    assert "across the 30 predeclared seeds" in _section("results")


def test_prose_only_wearable_offline_coding_fails(regen):
    data, _ = regen
    failed = data["continuity_benchmark"]["failed_cases"]
    assert [(r["research_class"], r["workload"], r["scenario_id"]) for r in failed] == [
        ("wearable", "offline_coding", "force_offline_coding_unsupported")
    ]
    assert sorted(data["findings"]["classes_never_failed"]) == ["desk", "local-creation", "mobile-docked"]


def test_prose_degraded_wifi_still_target_for_all_four_classes(regen):
    data, _ = regen
    assert data["findings"]["degraded_wifi_n_still_target"] == 4
    assert "All four classes still score \\texttt{target}" in _section("results")


def test_prose_gary_overlay_has_no_min_useful_miss(regen):
    data, _ = regen
    assert data["findings"]["gary_overlay_n_below_min_useful"] == 0


def test_prose_sinr_stub_constant_and_demand_shared_across_sites(regen):
    data, _ = regen
    assert len({r["sinr_db_stub"] for r in data["runs"]}) == 1
    sites = data["site_metric_panel"]["site_inclusion"]
    assert len({s["mean_demand_mbps"] for s in sites}) == 1
    assert len({s["digital_inclusion_readiness"] for s in sites}) > 1
