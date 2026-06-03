"""Export nodes/edges for diagram tooling."""
import json
from pathlib import Path

def export() -> Path:
    out = Path("results/diagrams_data")
    out.mkdir(parents=True, exist_ok=True)
    data = {
        "nodes": [
            {"id": "site_profiles", "module": "config.loader"},
            {"id": "scene_builder", "module": "scene_builder"},
            {"id": "geojson", "module": "scene_builder.build_geospatial"},
            {"id": "gltf", "module": "scene_builder.build_3d"},
        ],
        "edges": [
            {"from": "site_profiles", "to": "scene_builder"},
            {"from": "scene_builder", "to": "geojson"},
            {"from": "scene_builder", "to": "gltf"},
        ],
    }
    p = out / "nodes_edges.json"
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return p
