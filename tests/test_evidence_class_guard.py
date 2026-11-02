"""Calibrated promotion must refuse without owner measurement bundle."""
from __future__ import annotations

from pathlib import Path

import pytest

from seven_gc_twin.evidence_class_guard import (
    EvidenceClassPromotionError,
    assert_evidence_class_allowed,
    measurement_bundle_present,
    stamp_report_evidence,
)

ROOT = Path(__file__).resolve().parents[1]


def test_bundle_absent_in_checkout():
    assert measurement_bundle_present(ROOT) is False


def test_synthetic_allowed():
    assert assert_evidence_class_allowed("SYNTHETIC_SIM", root=ROOT) == "SYNTHETIC_SIM"


def test_calibrated_refused_without_bundle():
    with pytest.raises(EvidenceClassPromotionError, match="refuse promoting"):
        assert_evidence_class_allowed("CALIBRATED", root=ROOT)


def test_submitted_refused():
    with pytest.raises(EvidenceClassPromotionError, match="SUBMITTED"):
        assert_evidence_class_allowed("SYNTHETIC_SIM", root=ROOT, submitted=True)


def test_stamp_keeps_synthetic_and_human_false():
    stamped = stamp_report_evidence({"evidence_class": "SYNTHETIC_SIM", "n": 30}, root=ROOT)
    assert stamped["evidence_class"] == "SYNTHETIC_SIM"
    assert stamped["calibrated_measurements_present"] is False
    assert stamped["human_validation"] is False


def test_gap_ledger_honest():
    import json
    import subprocess

    gap = json.loads((ROOT / "paper" / "CALIBRATED_MEASUREMENT_GAP.json").read_text())
    tip = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    assert gap["evidence_class_current"] == "SYNTHETIC_SIM"
    assert gap["calibrated_measurements_present"] is False
    assert gap["submitted_claim"] is False
    assert gap.get("accepted_claim") is False
    assert gap["source_tip"].startswith(tip[:7])
    assert "HUMAN/RC2/V1 remain false" in gap["non_claims"]
    assert "Presence of gap rows does not authorize SUBMITTED/ACCEPTED" in gap["non_claims"]
