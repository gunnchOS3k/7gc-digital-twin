from site_buildings.evidence_flags import evidence_flags


def test_gaza_sensitive_privacy():
    f = evidence_flags("gaza")
    assert f["flags"]["no_sensitive_location_publish"]
    assert f["flags"]["child_protection_review_required"]
