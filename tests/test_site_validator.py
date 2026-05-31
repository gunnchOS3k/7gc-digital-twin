import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from seven_gc_twin.site_validator import validate_site
from seven_gc_twin.toy_scores import compute_toy_metric_bundle


def test_validate_missing_site_id():
    with pytest.raises(ValueError, match="site_id"):
        validate_site({})


def test_normalize_aliases():
    cfg = validate_site({"site_id": "gary", "display_name": "Gary"})
    assert cfg["name"] == "Gary"


def test_toy_metrics_keys():
    site = validate_site({"site_id": "x"})
    users = [{"demand_mbps": 10.0}, {"demand_mbps": 20.0}]
    m = compute_toy_metric_bundle(site, users, 0.9)
    assert "digital_equality_readiness_score" in m
