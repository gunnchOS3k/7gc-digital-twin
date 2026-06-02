"""Use case registry from site profiles."""
from __future__ import annotations

from .site_profiles import load_profile


def list_use_cases(site_id: str) -> list[dict]:
    p = load_profile(site_id)
    anchors = [{**uc, "kind": "anchor"} for uc in p["anchor_use_cases"]]
    resilience = [{**uc, "kind": "resilience"} for uc in p["resilience_use_cases"]]
    return anchors + resilience


def repos_for_site(site_id: str) -> set[str]:
    repos: set[str] = set()
    for uc in list_use_cases(site_id):
        repos.update(uc.get("repos_involved", []))
        repos.update(uc.get("ntn_resilience_requirements", []))
    return repos
