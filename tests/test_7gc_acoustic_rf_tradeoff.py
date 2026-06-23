from site_buildings.acoustic_scoring import acoustic_score
from site_buildings.rf_scoring import rf_tradeoff


def test_acoustic_rf_tradeoff():
    a = acoustic_score("flexible_classroom", "quiet_decompression")
    assert a["target"] == "high"
    r = rf_tradeoff("flexible_classroom")
    assert r["rely_on_wall_leakage"] is False
