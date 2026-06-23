"""Material class scoring for campus digital twin."""
from __future__ import annotations

MATERIAL_CLASSES = [
    "light-gauge steel framing with mineral wool",
    "double-stud acoustic partitions",
    "acoustic gypsum assemblies",
    "fiber cement / cement board",
    "mineral wool insulation",
    "acoustic sealant and gasketed doors",
    "low-VOC acoustic wall panels",
    "moisture-resistant flooring",
    "structured cabling pathways",
    "modular utility pods",
]


def score_material(material_class: str, site_id: str) -> dict:
    base = 0.7
    if site_id in ("guyana", "geelong") and "moisture" in material_class.lower():
        base += 0.1
    if site_id == "gaza" and "modular" in material_class.lower():
        base += 0.15
    if site_id == "graham_land":
        base = min(base, 0.5)  # conceptual only
    return {
        "material_class": material_class,
        "site_id": site_id,
        "suitability_score": round(min(base, 1.0), 2),
        "cost_class": "medium",
        "expert_review_needed": True,
        "evidence_status": "design assumption",
    }


def material_matrix(site_id: str) -> list[dict]:
    return [score_material(m, site_id) for m in MATERIAL_CLASSES]
