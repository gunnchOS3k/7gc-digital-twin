"""CLI for 7GC digital-twin campus operational pass."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .campus_reports import write_all_sites, write_site_bundle
from .integrations import integration_map
from .metrics import energy_per_bit_joules, jains_fairness, spectral_efficiency_bps_hz
from .report import research_card
from .scenario_engine import run_all_sites, run_scenario
from .scenario_loader import load_scenario
from .site_profiles import list_profile_sites, load_profile
from .sites import list_sites
from .toy_scores import compute_toy_metric_bundle
from .use_cases import list_use_cases


def _compute_summary(site_id: str) -> dict:
    scenario = load_scenario(site_id)
    site = scenario["site"]
    users = scenario["users"]
    demands = [u["demand_mbps"] for u in users]
    fairness = jains_fairness(demands)
    se = spectral_efficiency_bps_hz(site.get("radio", {}).get("sinr_db_stub", 10.0))
    energy = energy_per_bit_joules(
        site.get("energy_constraints", {}).get("power_w_stub", 5.0),
        max(sum(demands), 0.001) * 1e6,
    )
    latency_ms = site.get("qos", {}).get("latency_ms_stub", 25.0)
    return {
        "site_id": site_id,
        "is_flagship": site.get("is_flagship", False),
        "n_users": len(users),
        "jains_fairness": round(fairness, 4),
        "spectral_efficiency_bps_hz": round(se, 4),
        "energy_per_bit_j": round(energy, 8),
        "latency_ms_stub": latency_ms,
        "note": "research prototype — synthetic metrics only",
    }


def _toy_metrics(site_id: str) -> dict:
    scenario = load_scenario(site_id)
    demands = [u["demand_mbps"] for u in scenario["users"]]
    fairness = jains_fairness(demands)
    return compute_toy_metric_bundle(scenario["site"], scenario["users"], fairness)


def cmd_list_sites(_: argparse.Namespace) -> int:
    profiles = list_profile_sites()
    legacy = list_sites()
    for sid in sorted(set(profiles) | set(legacy)):
        print(sid)
    return 0


def cmd_show_site(args: argparse.Namespace) -> int:
    p = load_profile(args.site_id)
    print(json.dumps(p, indent=2))
    return 0


def cmd_list_use_cases(args: argparse.Namespace) -> int:
    for uc in list_use_cases(args.site_id):
        print(f"{uc['kind']}\t{uc['use_case_id']}\t{uc['name']}")
    return 0


def cmd_run_scenario(args: argparse.Namespace) -> int:
    result = run_scenario(args.site_id, args.scenario_id, mode=args.mode)
    print(json.dumps(result, indent=2))
    return 0


def cmd_run_all_sites(args: argparse.Namespace) -> int:
    results = run_all_sites(mode=args.mode)
    print(json.dumps(results, indent=2))
    write_all_sites(mode=args.mode)
    print("Wrote results/site_profiles/ for all sites")
    return 0


def cmd_make_campus_report(args: argparse.Namespace) -> int:
    bundle = write_site_bundle(args.site_id, mode=args.mode)
    print(json.dumps(bundle, indent=2))
    return 0


def cmd_export_site(args: argparse.Namespace) -> int:
    p = load_profile(args.site_id)
    out = Path("results/site_profiles") / f"{args.site_id}_profile.{args.format}"
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        out.write_text(json.dumps(p, indent=2) + "\n", encoding="utf-8")
    else:
        raise SystemExit(f"Unsupported format: {args.format}")
    print(f"Wrote {out}")
    return 0


def cmd_integration_map(args: argparse.Namespace) -> int:
    m = integration_map(args.site_id)
    print(json.dumps(m, indent=2))
    out = Path("results/site_profiles") / f"{args.site_id}_integration_map.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    summary = _compute_summary(args.site_id)
    print(json.dumps(summary, indent=2))
    out = Path("results") / f"{args.site_id}_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    summary = _compute_summary(args.site_id)
    out = Path("results") / f"{args.site_id}_export.{args.format}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    if not args.toy:
        raise SystemExit("Use --toy for synthetic metrics")
    metrics = _toy_metrics(args.site_id)
    print(json.dumps(metrics, indent=2))
    e2e = Path("results/e2e")
    e2e.mkdir(parents=True, exist_ok=True)
    path = e2e / f"{args.site_id}_toy_metrics.json"
    path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


def cmd_make_report(args: argparse.Namespace) -> int:
    summary = _compute_summary(args.site_id)
    toy = _toy_metrics(args.site_id)
    card = research_card(args.site_id, summary, toy)
    e2e = Path("results/e2e")
    e2e.mkdir(parents=True, exist_ok=True)
    md = e2e / f"{args.site_id}_research_card.md"
    md.write_text(card, encoding="utf-8")
    print(card)
    print(f"Wrote {md}")
    return 0


def cmd_validate_site(args: argparse.Namespace) -> int:
    from .config.loader import load_site_config
    from .config.validator import validate_site_config

    errs = validate_site_config(load_site_config(args.site_id))
    if errs:
        print("INVALID:", errs)
        return 1
    print("OK", args.site_id)
    return 0


def cmd_build_scene(args: argparse.Namespace) -> int:
    from .scene_builder import build_scene, CAMPUS_GEO
    from .scene.osm_overpass import merge_into_geojson

    r = build_scene(args.site_id, mode=args.mode)
    if args.mode == "open-data":
        c = CAMPUS_GEO[args.site_id]["center"]
        if merge_into_geojson(args.site_id, c):
            print("Overpass: updated community_anchors.geojson")
        else:
            print("Overpass: unavailable — synthetic anchors kept")
    print(json.dumps(r, indent=2))
    return 0


def cmd_build_all_scenes(args: argparse.Namespace) -> int:
    from .scene_builder import build_all_scenes

    results = build_all_scenes(mode=args.mode)
    print(json.dumps(results, indent=2))
    return 0


def cmd_export_scene(args: argparse.Namespace) -> int:
    from .scene_builder import build_scene

    build_scene(args.site_id, mode="synthetic-fixture")
    print(f"Exported scene layers under results/scenes/{args.site_id}/")
    return 0


def cmd_run_use_cases(args: argparse.Namespace) -> int:
    from .scene_builder import build_use_cases_layer

    paths = build_use_cases_layer(args.site_id, "synthetic-fixture")
    print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
    return 0


def cmd_run_bad_day(args: argparse.Namespace) -> int:
    from .bad_day_scenarios import run_bad_day

    print(json.dumps(run_bad_day(args.site_id, args.scenario_id, mode="smoke"), indent=2))
    return 0


def cmd_make_conference_artifacts(_: argparse.Namespace) -> int:
    from .scene_builder import integration_map_doc, make_conference_artifacts

    print(make_conference_artifacts())
    print(integration_map_doc())
    return 0


def cmd_integration_map_global(_: argparse.Namespace) -> int:
    from .scene_builder import integration_map_doc

    print(integration_map_doc())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="7GC digital twin CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-sites").set_defaults(func=cmd_list_sites)

    p_show = sub.add_parser("show-site")
    p_show.add_argument("site_id")
    p_show.set_defaults(func=cmd_show_site)

    p_uc = sub.add_parser("list-use-cases")
    p_uc.add_argument("site_id")
    p_uc.set_defaults(func=cmd_list_use_cases)

    p_run = sub.add_parser("run-scenario")
    p_run.add_argument("site_id")
    p_run.add_argument("scenario_id")
    p_run.add_argument("--mode", default="smoke")
    p_run.set_defaults(func=cmd_run_scenario)

    p_all = sub.add_parser("run-all-sites")
    p_all.add_argument("--mode", default="smoke")
    p_all.set_defaults(func=cmd_run_all_sites)

    p_campus = sub.add_parser("make-campus-report")
    p_campus.add_argument("site_id")
    p_campus.add_argument("--mode", default="smoke")
    p_campus.set_defaults(func=cmd_make_campus_report)

    p_exp_site = sub.add_parser("export-site")
    p_exp_site.add_argument("site_id")
    p_exp_site.add_argument("--format", default="json", choices=["json"])
    p_exp_site.set_defaults(func=cmd_export_site)

    p_map = sub.add_parser("integration-map")
    p_map.add_argument("site_id", nargs="?", default=None)
    p_map.set_defaults(func=lambda a: cmd_integration_map(a) if a.site_id else cmd_integration_map_global(a))

    p_val = sub.add_parser("validate-site")
    p_val.add_argument("site_id")
    p_val.set_defaults(func=cmd_validate_site)

    p_bs = sub.add_parser("build-scene")
    p_bs.add_argument("site_id")
    p_bs.add_argument("--mode", default="synthetic-fixture", choices=["synthetic-fixture", "open-data"])
    p_bs.set_defaults(func=cmd_build_scene)

    p_bsa = sub.add_parser("build-all-scenes")
    p_bsa.add_argument("--mode", default="synthetic-fixture")
    p_bsa.set_defaults(func=cmd_build_all_scenes)

    p_es = sub.add_parser("export-scene")
    p_es.add_argument("site_id")
    p_es.add_argument("--formats", default="geojson,gltf")
    p_es.set_defaults(func=cmd_export_scene)

    p_ruc = sub.add_parser("run-use-cases")
    p_ruc.add_argument("site_id")
    p_ruc.set_defaults(func=cmd_run_use_cases)

    p_rbd = sub.add_parser("run-bad-day")
    p_rbd.add_argument("site_id")
    p_rbd.add_argument("scenario_id")
    p_rbd.set_defaults(func=cmd_run_bad_day)

    sub.add_parser("make-conference-artifacts").set_defaults(func=cmd_make_conference_artifacts)

    p_sum = sub.add_parser("summarize")
    p_sum.add_argument("site_id")
    p_sum.set_defaults(func=cmd_summarize)

    p_exp = sub.add_parser("export")
    p_exp.add_argument("site_id")
    p_exp.add_argument("--format", default="json", choices=["json"])
    p_exp.set_defaults(func=cmd_export)

    p_met = sub.add_parser("metrics")
    p_met.add_argument("site_id")
    p_met.add_argument("--toy", action="store_true")
    p_met.set_defaults(func=cmd_metrics)

    p_rep = sub.add_parser("make-report")
    p_rep.add_argument("site_id")
    p_rep.set_defaults(func=cmd_make_report)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
