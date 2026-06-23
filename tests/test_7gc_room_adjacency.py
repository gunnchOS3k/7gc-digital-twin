from site_buildings.room_adjacency import build_adjacency
from site_buildings.site_registry import SITE_IDS


def test_adjacency_edges():
    for sid in SITE_IDS:
        adj = build_adjacency(sid)
        assert len(adj["edges"]) >= len(adj["nodes"]) - 1
