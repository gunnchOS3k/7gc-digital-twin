"""Refuse SYNTHETIC_SIM → CALIBRATED promotion without an owner measurement bundle.

Engineering may deepen honesty and synthetic reproduce paths. Inventing RF /
sensor numbers to flip evidence_class is forbidden.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

ALLOWED_WITHOUT_BUNDLE = frozenset({"SYNTHETIC_SIM", "SIMULATED", "UNCALIBRATED"})
CALIBRATED_CLASSES = frozenset({"CALIBRATED", "CALIBRATED_SIM", "FIELD_RF", "MEASURED"})


class EvidenceClassPromotionError(ValueError):
    """Raised when a report attempts calibrated class without provenance."""


def measurement_bundle_present(root: Path | None = None) -> bool:
    """True only when owner-supplied calibrated bundle + provenance SHA exist."""
    base = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    marker = base / "paper" / "calibrated_measurements" / "PROVENANCE.sha256"
    if not marker.is_file():
        return False
    digest = marker.read_text(encoding="utf-8").strip()
    return len(digest) >= 64 and all(c in "0123456789abcdefABCDEF" for c in digest[:64])


def assert_evidence_class_allowed(
    evidence_class: str,
    *,
    root: Path | None = None,
    submitted: bool = False,
) -> str:
    """Return normalized class or raise if promotion/submission is unauthorized."""
    cls = str(evidence_class or "").strip().upper()
    if submitted:
        raise EvidenceClassPromotionError(
            "SUBMITTED claim refused: packet forbids self-SUBMITTED without owner stamp"
        )
    if cls in CALIBRATED_CLASSES and not measurement_bundle_present(root):
        raise EvidenceClassPromotionError(
            f"refuse promoting to {cls}: calibrated measurement bundle missing "
            "(paper/calibrated_measurements/PROVENANCE.sha256)"
        )
    if cls not in ALLOWED_WITHOUT_BUNDLE and cls not in CALIBRATED_CLASSES:
        raise EvidenceClassPromotionError(f"unknown evidence_class={cls!r}")
    return cls


def stamp_report_evidence(
    report: dict[str, Any],
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    """Copy report with guarded evidence_class; never invents calibrated fields."""
    out = dict(report)
    cls = assert_evidence_class_allowed(
        str(out.get("evidence_class", "SYNTHETIC_SIM")),
        root=root,
        submitted=bool(out.get("submitted") or out.get("submitted_claim")),
    )
    out["evidence_class"] = cls
    out["calibrated_measurements_present"] = measurement_bundle_present(root)
    out["human_validation"] = False
    return out
