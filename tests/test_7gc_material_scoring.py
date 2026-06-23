from site_buildings.material_scoring import material_matrix
from site_buildings.site_registry import SITE_IDS


def test_material_matrix_scores():
    for sid in SITE_IDS:
        mats = material_matrix(sid)
        assert len(mats) >= 5
        assert all(0 <= m["suitability_score"] <= 1 for m in mats)
