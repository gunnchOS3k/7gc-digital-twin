"""Acoustic isolation scoring."""
from __future__ import annotations


def acoustic_score(room_a: str, room_b: str) -> dict:
    quiet_rooms = {"quiet_decompression", "hybrid_learning_corner", "design_critique_room"}
    high = room_a in quiet_rooms or room_b in quiet_rooms
    return {
        "room_a": room_a,
        "room_b": room_b,
        "target": "high" if high else "moderate",
        "strategy": "double-stud acoustic partition with gasketed door",
        "note": "sound-isolated — not fully soundproof",
        "evidence_status": "design assumption",
    }
