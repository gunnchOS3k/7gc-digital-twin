"""Export bundle for campus digital twin artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from site_buildings.evidence_flags import evidence_flags
from site_buildings.floorplan_model import build_floorplan_blocks
from site_buildings.material_scoring import material_matrix
from site_buildings.power_model import power_model
from site_buildings.room_adjacency import build_adjacency
from site_buildings.site_registry import SITE_IDS
from site_buildings.svg_floorplan_export import export_svg


def export_site(site_id: str, out_root: Path) -> dict[str, Path]:
    out = out_root / site_id
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    adj = build_adjacency(site_id)
    p = out / "room_adjacency.json"
    p.write_text(json.dumps(adj, indent=2), encoding="utf-8")
    paths["adjacency"] = p

    svg = export_svg(site_id)
    p = out / "floorplan_blocks.svg"
    p.write_text(svg, encoding="utf-8")
    paths["svg"] = p

    mats = material_matrix(site_id)
    p = out / "material_matrix.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=mats[0].keys())
        w.writeheader()
        w.writerows(mats)
    paths["materials"] = p

    summary = {
        "site_id": site_id,
        "floorplan": build_floorplan_blocks(site_id),
        "power": power_model(site_id),
        "evidence": evidence_flags(site_id),
    }
    p = out / "design_summary.md"
    p.write_text(
        f"# Design Summary — {site_id}\n\n> Conceptual only — not for construction\n\n```yaml\n{yaml.dump(summary)}```\n",
        encoding="utf-8",
    )
    paths["summary"] = p

    p = out / "config_snapshot.yaml"
    p.write_text(yaml.dump(summary, sort_keys=False), encoding="utf-8")
    paths["config"] = p

    return paths


def export_all(out_root: Path | None = None) -> dict[str, dict[str, Path]]:
    root = out_root or Path("results/exports")
    return {sid: export_site(sid, root) for sid in SITE_IDS}
