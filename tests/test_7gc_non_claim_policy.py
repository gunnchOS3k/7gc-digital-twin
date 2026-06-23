from site_buildings.evidence_flags import evidence_flags


def test_non_claim_graham_land():
    f = evidence_flags("graham_land")
    assert f["flags"]["no_antarctic_construction_claim"]
