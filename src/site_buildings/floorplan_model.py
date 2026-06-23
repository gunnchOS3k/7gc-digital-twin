"""Block floor plan model for campus digital twin."""
from __future__ import annotations

from typing import Any

from site_buildings.site_registry import get_site


def build_floorplan_blocks(site_id: str, footprint: str = "semi_permanent_hub") -> dict[str, Any]:
    site = get_site(site_id)
    rooms = site["rooms"]
    if footprint == "minimum_pilot":
        rooms = rooms[:4]
    elif footprint == "full_campus":
        rooms = rooms
    else:
        rooms = rooms[:8]

    block_w, block_h = 120, 80
    blocks = []
    cols = 4
    for i, room in enumerate(rooms):
        row, col = divmod(i, cols)
        blocks.append(
            {
                "id": room,
                "x": col * (block_w + 20),
                "y": row * (block_h + 20),
                "width": block_w,
                "height": block_h,
                "label": room.replace("_", " "),
            }
        )
    return {
        "site_id": site_id,
        "footprint": footprint,
        "blocks": blocks,
        "label": "Conceptual only — not for construction",
        "evidence_status": "design assumption",
    }
