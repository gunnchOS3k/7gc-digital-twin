"""Public data source registry."""
SOURCES = {
    "openstreetmap": {"url": "https://www.openstreetmap.org", "use": "roads/buildings/POI"},
    "overpass_api": {"url": "https://wiki.openstreetmap.org/wiki/Overpass_API", "use": "optional ingest"},
}
