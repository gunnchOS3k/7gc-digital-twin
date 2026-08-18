"""Site, scene, and experiment schema helpers.

These fields describe **research scenario environments**, not community deployments.
Gary is the flagship scenario. Ghana, Guyana, Gaza, Geelong, Graham Land, and Germany
are comparative scenario environments used for RQ1 profile/benchmark work.
"""
from __future__ import annotations

REQUIRED_SCENE_FIELDS = (
    "site_id",
    "display_name",
    "anchor_use_cases",
    "resilience_use_cases",
    "bad_day_scenarios",
    "no_foreign_savior_guardrails",
)

# Documented site YAML keys (configs/sites/*.yaml). Not all are required yet;
# missing keys are filled by site_validator.normalize_site.
SITE_YAML_FIELDS = {
    "site_id": "stable identifier; also the scenario-environment name",
    "display_name": "human-readable label",
    "node_role": "flagship_scenario | comparative_scenario",
    "is_flagship": "true only for gary",
    "scenario_environment_not_community_deployment": "must be true for all 7GC names",
    "spectrum": "planning bands and constraint class (synthetic unless provenance says otherwise)",
    "population": "synthetic user counts only — no PII",
    "connectivity": "terrestrial / ntn_fallback flags for scenario composition",
    "radio": "optional synthetic radio stubs (sinr_db_stub); never a field measurement",
    "qos": "optional synthetic latency stubs",
    "energy_constraints": "optional power_w_stub",
    "workload": "optional demand mix (learn/create/sense fractions)",
    "mobility": "optional static/pedestrian mix",
    "failure_model": "optional named failure families (outage, congestion, power)",
    "metrics": "which RQ1 metrics to emit",
}

REQUIRED_EXPERIMENT_FIELDS = (
    "experiment_id",
    "research_question",
    "site_id",
    "mode",
    "seeds",
    "metrics",
    "non_claims",
)

FLAGSHIP_SITE_ID = "gary"
SCENARIO_ENVIRONMENT_IDS = (
    "ghana",
    "guyana",
    "gaza",
    "geelong",
    "graham_land",
    "germany",
)
ALL_SITE_IDS = (FLAGSHIP_SITE_ID,) + SCENARIO_ENVIRONMENT_IDS

METRIC_FAMILIES = (
    "workload",
    "compute",
    "radio",
    "failure",
    "mobility",
    "inclusion",
)
