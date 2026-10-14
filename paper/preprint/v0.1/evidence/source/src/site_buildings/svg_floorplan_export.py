"""SVG block floor plan export."""
from __future__ import annotations

from site_buildings.floorplan_model import build_floorplan_blocks


def export_svg(site_id: str, footprint: str = "semi_permanent_hub") -> str:
    fp = build_floorplan_blocks(site_id, footprint)
    blocks = fp["blocks"]
    if not blocks:
        return "<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'></svg>"
    max_x = max(b["x"] + b["width"] for b in blocks) + 40
    max_y = max(b["y"] + b["height"] for b in blocks) + 60
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{max_x}" height="{max_y}">',
        f'<text x="10" y="20" font-size="12">{fp["label"]}</text>',
    ]
    for b in blocks:
        lines.append(
            f'<rect x="{b["x"]}" y="{b["y"]+30}" width="{b["width"]}" height="{b["height"]}" '
            f'fill="#e8f0fe" stroke="#333"/>'
        )
        lines.append(
            f'<text x="{b["x"]+5}" y="{b["y"]+55}" font-size="10">{b["label"][:18]}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)
