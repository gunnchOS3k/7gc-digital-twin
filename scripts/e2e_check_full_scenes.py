#!/usr/bin/env python3
"""Verify full scene pipeline artifacts exist."""
from pathlib import Path

SITES = ["gary", "ghana", "guyana", "gaza", "geelong", "graham_land", "germany"]
REQUIRED = [
    "geo/base_layers.geojson",
    "3d/scene.gltf",
    "3d/scene_manifest.json",
    "connectivity/connectivity_graph.json",
    "population/synthetic_population.json",
    "use_cases/use_case_register.json",
    "reports/campus_report.md",
    "waike/learning_tracks.md",
    "edge_io/measurement_plan.md",
    "ntn/resilience_scenario.yaml",
    "ai_ran/campus_ai_ran_profile.yaml",
    "beam_selection/radio_profile.yaml",
]
CONFERENCE = [
    "results/conference/7gc_scene_table.md",
    "results/conference/7gc_use_case_table.md",
    "results/conference/7gc_evidence_maturity_table.md",
]
DIAGRAM = "docs/diagrams/architecture_full_scene_pipeline.mmd"

errs = []
for site in SITES:
    base = Path("results/scenes") / site
    for rel in REQUIRED:
        if not (base / rel).exists():
            errs.append(f"{site}/{rel}")
for c in CONFERENCE:
    if not Path(c).exists():
        errs.append(c)
if not Path(DIAGRAM).exists():
    errs.append(DIAGRAM)
if errs:
    print("FAIL missing:", *errs, sep="\n ")
    raise SystemExit(1)
print("PASS full scene artifacts")
