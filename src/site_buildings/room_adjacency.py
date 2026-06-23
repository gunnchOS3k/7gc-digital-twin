"""Room adjacency graph builder for campus digital twin."""
from __future__ import annotations

from typing import Any

from site_buildings.site_registry import get_site


def build_adjacency(site_id: str) -> dict[str, Any]:
    site = get_site(site_id)
    rooms = site["rooms"]
    edges: list[dict[str, str]] = []
    for i in range(len(rooms) - 1):
        edges.append({"from": rooms[i], "to": rooms[i + 1], "type": "adjacent"})
    # hub connections
    hub = "welcome_intake"
    for r in rooms[1:4]:
        edges.append({"from": hub, "to": r, "type": "hub"})
    return {
        "site_id": site_id,
        "nodes": [{"id": r, "label": r.replace("_", " ")} for r in rooms],
        "edges": edges,
        "evidence_status": "design assumption",
    }
