"""Load grounded 7GC campus site profiles (YAML)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROFILES_DIR = Path(__file__).resolve().parents[2] / "configs" / "site_profiles"

REQUIRED_TOP = (
    "site_id",
    "display_name",
    "anchor_use_cases",
    "resilience_use_cases",
    "bad_day_scenarios",
    "metrics_definitions",
    "no_foreign_savior_guardrails",
    "evidence_to_collect",
    "source_assumptions",
)


def list_profile_sites() -> list[str]:
    return sorted(p.stem for p in PROFILES_DIR.glob("*.yaml"))


def load_profile(site_id: str) -> dict[str, Any]:
    path = PROFILES_DIR / f"{site_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Unknown site profile: {site_id} ({path})")
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data.get("site_id") != site_id:
        raise ValueError(f"site_id mismatch in {path}")
    for key in REQUIRED_TOP:
        if key not in data:
            raise ValueError(f"Missing required key {key} in {path}")
    if len(data["anchor_use_cases"]) < 3:
        raise ValueError(f"Need >=3 anchor use cases in {path}")
    if len(data["resilience_use_cases"]) < 2:
        raise ValueError(f"Need >=2 resilience use cases in {path}")
    return data


def validate_all_profiles() -> list[str]:
    errors: list[str] = []
    for sid in list_profile_sites():
        try:
            load_profile(sid)
        except (OSError, ValueError, yaml.YAMLError) as e:
            errors.append(f"{sid}: {e}")
    return errors
