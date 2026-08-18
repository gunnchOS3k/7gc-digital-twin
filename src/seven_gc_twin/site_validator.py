"""Validate 7GC site YAML configs with friendly errors."""
from __future__ import annotations

REQUIRED = ("site_id",)
RECOMMENDED = (
    "name",
    "region",
    "environment_type",
    "population_assumptions",
    "device_mix",
    "spectrum_constraints",
    "energy_constraints",
    "backhaul_assumptions",
    "privacy_constraints",
)

ALIASES = {"display_name": "name", "population": "population_assumptions", "spectrum": "spectrum_constraints"}


def normalize_site(data: dict) -> dict:
    out = dict(data)
    for old, new in ALIASES.items():
        if old in out and new not in out:
            out[new] = out[old]
    if "name" not in out and "site_id" in out:
        out["name"] = out["site_id"].replace("_", " ").title()
    out.setdefault("region", "unknown")
    out.setdefault("environment_type", "urban_community")
    out.setdefault("population_assumptions", out.get("population", {"synthetic_users": 100}))
    out.setdefault("device_mix", {"static_pct": 0.7, "mobile_pct": 0.3})
    out.setdefault("spectrum_constraints", out.get("spectrum", {"bands_ghz": [3.5]}))
    out.setdefault("energy_constraints", {"power_w_stub": 5.0})
    out.setdefault("backhaul_assumptions", {"capacity_gbps_stub": 1.0})
    out.setdefault("privacy_constraints", {"synthetic_only": True, "no_pii": True})
    out.setdefault("scenario_environment_not_community_deployment", True)
    if out.get("site_id") == "gary":
        out.setdefault("is_flagship", True)
        out.setdefault("node_role", "flagship_scenario")
    else:
        out.setdefault("is_flagship", False)
        out.setdefault("node_role", "comparative_scenario")
    return out


def validate_site(data: dict, path: str = "") -> dict:
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"Site config {path}: missing required field(s): {', '.join(missing)}")
    normalized = normalize_site(data)
    if normalized.get("site_id") != data.get("site_id"):
        raise ValueError(f"Site config {path}: site_id mismatch")
    return normalized
