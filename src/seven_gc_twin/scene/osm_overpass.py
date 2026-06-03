"""Optional OpenStreetMap Overpass ingest — network required."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path


def try_fetch_pois(center_lon: float, center_lat: float, delta: float = 0.01) -> dict | None:
    """Return GeoJSON FeatureCollection or None if network/unavailable."""
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"~"school|library|hospital"]({center_lat-delta},{center_lon-delta},{center_lat+delta},{center_lon+delta});
    );
    out center;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        req = urllib.request.Request(url, data=query.encode(), method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = json.loads(resp.read().decode())
        features = []
        for el in raw.get("elements", [])[:20]:
            if "lat" in el and "lon" in el:
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [el["lon"], el["lat"]]},
                    "properties": {"amenity": el.get("tags", {}).get("amenity"), "source": "overpass"},
                })
        return {"type": "FeatureCollection", "features": features, "properties": {"evidence_status": "open_data_backed"}}
    except Exception:
        return None


def merge_into_geojson(site_id: str, center: list[float]) -> bool:
    """If Overpass succeeds, write community_anchors.geojson with open_data_backed."""
    fc = try_fetch_pois(center[0], center[1])
    if not fc or not fc.get("features"):
        return False
    path = Path("results/scenes") / site_id / "geo" / "community_anchors.geojson"
    path.parent.mkdir(parents=True, exist_ok=True)
    fc["properties"] = {"site_id": site_id, "evidence_status": "open_data_backed", "data_mode": "open-data"}
    path.write_text(json.dumps(fc, indent=2) + "\n", encoding="utf-8")
    return True
