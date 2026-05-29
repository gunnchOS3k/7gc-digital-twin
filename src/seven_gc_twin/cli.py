"""CLI for 7GC digital twin research scaffold."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from seven_gc_twin.scenario_loader import load_scenario
from seven_gc_twin.sites import list_sites, load_site
from seven_gc_twin.metrics import jains_fairness, energy_per_bit_joules
from seven_gc_twin.visualization_stub import site_summary_table


def cmd_list_sites(_: argparse.Namespace) -> None:
    for sid in list_sites():
        cfg = load_site(sid)
        flag = " [flagship]" if cfg.get("is_flagship") else ""
        print(f"{sid}{flag}")


def cmd_summarize(args: argparse.Namespace) -> None:
    scenario = load_scenario(args.site_id)
    summary = site_summary_table([scenario])[0]
    demands = [u["demand_mbps"] for u in scenario["users"][:20]]
    summary["jain_fairness_toy"] = round(jains_fairness(demands), 4)
    summary["energy_per_bit_toy"] = energy_per_bit_joules(10.0, 1e6)
    print(json.dumps(summary, indent=2))


def cmd_export(args: argparse.Namespace) -> None:
    scenario = load_scenario(args.site_id)
    out = {"site": scenario["site"], "user_count": len(scenario["users"])}
    if args.format == "json":
        print(json.dumps(out, indent=2))
    else:
        print(out)


def main() -> None:
    p = argparse.ArgumentParser(description="7GC digital twin CLI (research scaffold)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list-sites").set_defaults(func=cmd_list_sites)
    s = sub.add_parser("summarize")
    s.add_argument("site_id")
    s.set_defaults(func=cmd_summarize)
    e = sub.add_parser("export")
    e.add_argument("site_id")
    e.add_argument("--format", default="json", choices=["json"])
    e.set_defaults(func=cmd_export)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
