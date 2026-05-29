import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from seven_gc_twin.sites import list_sites, load_site


def test_all_sites_load():
    for sid in list_sites():
        cfg = load_site(sid)
        assert cfg["site_id"] == sid


def test_gary_is_flagship():
    assert load_site("gary").get("is_flagship") is True
