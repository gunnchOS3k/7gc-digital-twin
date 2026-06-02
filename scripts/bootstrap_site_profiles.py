#!/usr/bin/env python3
"""Generate campus YAML configs across 7GC repos (machine-readable, source-backed)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

SPINE = Path("/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos")
ORCH = Path("/Users/gunnchos/Downloads/gunnchos-7gc-grounded-use-cases-operational-pass")

SITES = ["gary", "ghana", "guyana", "gaza", "geelong", "graham_land", "germany"]

REPOS_INVOLVED = [
    "7gc-digital-twin", "edge-io-measurement-node", "ntn-resilience-sim",
    "waike-research-ops", "gunnchos-device-os", "gunnchos-hardware-industrial-design",
    "spectrumx-ai-ran-gary", "readygary-6g-beam-selection", "gunnchAI3k",
]

SITE_META = {
    "gary": {
        "display_name": "Gary, Indiana",
        "region_type": "urban_midwest_us",
        "campus_role": "Flagship community digital equality and family/community technology node",
        "digital_divide_context": "Spectrum-constrained urban connectivity with affordability and trust barriers",
        "access_barriers": ["affordability", "legacy infrastructure", "device gaps"],
        "affordability_barriers": ["monthly plan cost", "device replacement cycles"],
        "device_barriers": ["shared household devices", "older phones"],
        "skills_barriers": ["digital navigation", "cyber hygiene"],
        "trust_privacy_barriers": ["surveillance concerns", "data misuse fear"],
        "power_energy_barriers": ["grid stability during storms"],
        "resilience_barriers": ["outage learning disruption", "small business downtime"],
        "language_accessibility_barriers": ["multilingual households", "accessibility needs"],
        "local_governance": "Community steering with schools, libraries, and local partners",
        "steering_roles": ["community liaison", "school tech lead", "library anchor", "youth mentor", "small business rep"],
        "partner_types": ["school district", "library", "community org", "local ISP partner"],
        "guardrails": [
            "No outside vendor decides community priorities",
            "Residents review metrics before public claims",
            "Youth co-design for family tech nights",
            "No PII in public artifacts",
            "Competition data never mixed with community pilots",
        ],
        "anchors": [
            ("gary_youth_builder", "Youth builder pathway", "Youth lack safe paths into wireless research", "Need reproducible lab-to-GitHub pipeline", "Informal online tutorials only", "WAIKE + 7GC twin scenarios", "Extractive volunteering", "school", "rubric samples", ["waike-research-ops", "7gc-digital-twin"]),
            ("gary_family_nav", "Family digital navigation", "Families struggle with device/setup trust", "Need privacy-first onboarding", "Ad hoc help desks", "Device OS kiosk + Edge-IO smoke", "Surveillance-style monitoring", "library", "consent logs", ["gunnchos-device-os", "edge-io-measurement-node"]),
            ("gary_smb_starter", "Small business digital starter", "SMBs lose revenue during outages", "Need resilience + fair AI-RAN", "Consumer hotspots", "NTN sim + AI-RAN policy smoke", "Over-promising uptime", "chamber partner", "outage drill notes", ["spectrumx-ai-ran-gary", "ntn-resilience-sim"]),
        ],
        "resilience": [
            ("gary_outage_learning", "Outage learning cache", "School day", "Neighborhood outage", "Multi-day blackout", "Cache sync day", "Offline lesson bundles + NTN fallback sim", ["service_continuity", "priority_preservation"], "school fleet mode", "aggregate latency only", ["waike", "ntn", "device-os"]),
            ("gary_storm_fairness", "Storm fairness stress", "Fair weekday", "Storm congestion", "Emergency prioritization", "Recovery fairness audit", "AI-RAN fairness policy smoke", ["fairness_index", "unmet_demand"], "URLLC lab mode", "no location traces", ["spectrumx", "7gc"]),
        ],
        "bad_days": ["neighborhood_outage", "storm_congestion", "school_bandwidth_collapse", "library_hotspot_overload", "smb_payment_system_down"],
        "sources": [("itu_imt2030", "IMT-2030 framework for capability targets", "https://www.itu.int", "medium", True)],
    },
    "ghana": {
        "display_name": "Ghana",
        "region_type": "west_africa_mobile_first",
        "campus_role": "Mobile-first, power-aware, affordability-aware inclusion node",
        "digital_divide_context": "Mobile-first access with power and cost constraints",
        "access_barriers": ["rural backhaul", "power interruptions"],
        "affordability_barriers": ["prepaid data costs", "device import costs"],
        "device_barriers": ["feature phones mixed with smartphones"],
        "skills_barriers": ["workforce digital skills gaps"],
        "trust_privacy_barriers": ["mobile money fraud fears"],
        "power_energy_barriers": ["solar hub variability", "grid outages"],
        "resilience_barriers": ["backhaul failure during storms"],
        "language_accessibility_barriers": ["multilingual education content"],
        "local_governance": "Community + vocational school co-governance",
        "steering_roles": ["vocational instructor", "solar hub operator", "youth apprentice", "telehealth liaison", "local gov ICT"],
        "partner_types": ["vocational school", "solar hub", "health clinic ICT"],
        "guardrails": ["Local instructors own curriculum pacing", "No donor-driven tech dumping", "Power metrics include solar reality", "Mobile money hygiene taught before telemetry", "Export only aggregates"],
        "anchors": [
            ("ghana_mobile_workforce", "Mobile-first workforce", "Youth unemployment without digital trades", "Skills-to-repo gap", "Paper certificates only", "WAIKE workforce track", "Training without jobs pathway", "vocational school", "portfolio rubric", ["waike-research-ops"]),
            ("ghana_solar_hub", "Solar learning hub ops", "Hubs fail when power unstable", "Need power-aware scheduling", "Manual generator logs", "Device low-power modes + NTN", "Ignoring battery wear", "solar operator", "power logs", ["gunnchos-device-os", "ntn-resilience-sim"]),
            ("ghana_mobile_money_sec", "Mobile money cybersecurity", "Fraud erodes trust", "Need security education + measurement", "Word of mouth only", "Edge-IO aggregate probes", "Collecting transaction PII", "clinic ICT", "training attendance", ["edge-io-measurement-node", "waike-research-ops"]),
        ],
        "resilience": [
            ("ghana_power_backhaul", "Power/backhaul failure", "Normal school day", "Backhaul down", "Regional outage", "Solar recovery", "Offline cache + satellite window", ["continuity", "recovery_time"], "low_bandwidth", "aggregate only", ["ntn", "device-os"]),
            ("ghana_heat_derate", "Heat derate day", "Cool morning labs", "Midday thermal throttle", "Extended heat wave", "Night batch sync", "Power-aware AI-RAN", ["energy_score"], "thermal guard", "no student IDs", ["spectrumx", "hardware"]),
        ],
        "bad_days": ["backhaul_cut", "solar_low", "mobile_money_phishing_spike", "exam_day_congestion", "clinic_telehealth_drop"],
        "sources": [("gsma_mobile", "Mobile connectivity statistics (public reports)", "https://www.gsma.com", "low", True)],
    },
}

# Fill remaining sites with template expansion
for sid, role, ctx in [
    ("guyana", "Hinterland connectivity, Indigenous/community-governed data, e-services, flood resilience", "Riverine and hinterland access gaps"),
    ("gaza", "Remote-first humanitarian education continuity and no-data-harm crisis resilience", "Crisis connectivity with extreme privacy risk"),
    ("geelong", "Inclusive smart-city, accessibility, youth creative-tech", "Accessibility and youth creative inclusion"),
    ("graham_land", "Polar/outpost NTN, low-power, offline-first scientific workflow", "Extreme environment delayed sync"),
    ("germany", "Privacy/security equity, Industry 4.0, EU standards transfer", "Privacy-first digital service confidence"),
]:
    if sid not in SITE_META:
        SITE_META[sid] = {
            "display_name": sid.replace("_", " ").title(),
            "region_type": f"campus_{sid}",
            "campus_role": role,
            "digital_divide_context": ctx,
            "access_barriers": ["geography", "cost", "skills"],
            "affordability_barriers": ["hardware cost", "service fees"],
            "device_barriers": ["shared devices", "ruggedness needs"],
            "skills_barriers": ["trainer capacity", "language"],
            "trust_privacy_barriers": ["data harm risk", "governance trust"],
            "power_energy_barriers": ["outage", "remote power"],
            "resilience_barriers": ["disaster", "congestion"],
            "language_accessibility_barriers": ["localization", "a11y"],
            "local_governance": "Community steering circle required before deployment",
            "steering_roles": ["local lead", "ethics reviewer", "technical mentor", "youth rep", "partner liaison"],
            "partner_types": ["school", "municipality", "NGO", "research partner"],
            "guardrails": [
                "Community approves metrics",
                "No foreign savior framing in reports",
                "Consent before measurement",
                "Aggregate-only public exports",
                "Mark assumptions needing local validation",
            ],
            "anchors": [
                (f"{sid}_anchor_a", f"{sid} anchor A", "Human access gap", "Technical gap", "Workaround", "7GC intervention", "Risk if bad", "local partner", "evidence list", REPOS_INVOLVED[:3]),
                (f"{sid}_anchor_b", f"{sid} anchor B", "Human B", "Technical B", "Workaround B", "Intervention B", "Risk B", "partner B", "evidence B", REPOS_INVOLVED[3:6]),
                (f"{sid}_anchor_c", f"{sid} anchor C", "Human C", "Technical C", "Workaround C", "Intervention C", "Risk C", "partner C", "evidence C", REPOS_INVOLVED[6:9]),
            ],
            "resilience": [
                (f"{sid}_res_a", f"{sid} resilience A", "Normal", "Bad", "Worst", "Recovery", "7GC response", ["continuity"], "device req", "edge req", ["ntn", "edge-io"]),
                (f"{sid}_res_b", f"{sid} resilience B", "Normal B", "Bad B", "Worst B", "Recovery B", "Response B", ["recovery_time"], "device B", "edge B", ["waike", "7gc"]),
            ],
            "bad_days": [f"{sid}_flood", f"{sid}_outage", f"{sid}_congestion", f"{sid}_privacy_incident", f"{sid}_power_loss"],
            "sources": [(f"{sid}_assumption_1", "Public resilience framework reference", "https://www.itu.int", "low", True)],
        }


def _anchor_uc(tup):
    uid, name, human, tech, workaround, intervention, risk, partner, evidence, repos = tup
    return {
        "use_case_id": uid,
        "name": name,
        "human_problem": human,
        "technical_problem": tech,
        "current_workaround": workaround,
        "7gc_intervention": intervention,
        "risks_if_done_badly": risk,
        "required_local_partner": partner,
        "evidence_to_collect": [evidence] if isinstance(evidence, str) else evidence,
        "repos_involved": repos,
    }


def _resilience_uc(tup):
    uid, name, normal, bad, worst, recovery, response, metrics, dev, edge, repos = tup
    return {
        "use_case_id": uid,
        "name": name,
        "normal_day": normal,
        "bad_day": bad,
        "worst_day": worst,
        "recovery_day": recovery,
        "7gc_response": response,
        "metrics": metrics,
        "device_and_os_requirements": dev,
        "edge_io_measurement_requirements": edge,
        "waike_learning_tracks": [f"waike_{uid}"],
        "ntn_resilience_requirements": repos,
        "ai_ran_requirements": ["spectrumx-ai-ran-gary"] if "spectrumx" in str(repos) else ["spectrumx-ai-ran-gary"],
        "beam_selection_requirements": ["readygary-6g-beam-selection"],
        "privacy_and_ethics": "Aggregate-only; local ethics review required",
        "consent_requirements": "Explicit opt-in before any measurement",
        "data_never_collected": ["precise location of minors", "biometrics", "raw message content"],
        "retention_policy": "Minimum necessary; delete on request where applicable",
        "local_review_needed": True,
    }


def build_site_profile(site_id: str) -> dict:
    m = SITE_META[site_id]
    bad_day_scenarios = []
    for i, bid in enumerate(m["bad_days"][:5]):
        bad_day_scenarios.append({
            "scenario_id": bid,
            "description": f"Bad-day scenario {i+1} for {site_id}",
            "trigger": "configurable stress event",
            "metrics": ["service_continuity", "unmet_demand_proxy", "recovery_time_proxy"],
            "needs_local_validation": True,
        })
    metrics = [
        {"metric_id": "digital_inclusion_readiness", "description": "Inclusion readiness (smoke composite)", "scale": "0-1"},
        {"metric_id": "access_barrier_score", "description": "Access barrier pressure", "scale": "0-1"},
        {"metric_id": "affordability_pressure", "description": "Affordability pressure", "scale": "0-1"},
        {"metric_id": "power_resilience_risk", "description": "Power/resilience risk", "scale": "0-1"},
        {"metric_id": "privacy_data_harm_risk", "description": "Privacy/data harm risk", "scale": "0-1"},
    ]
    evidence = [
        {"item_id": f"{site_id}_ev_{i}", "description": f"Field validation item {i+1}", "requires_local_validation": True}
        for i in range(5)
    ]
    sources = [
        {
            "source_id": s[0],
            "claim": s[1],
            "url_or_reference": s[2],
            "confidence": s[3],
            "needs_local_validation": s[4],
        }
        for s in m["sources"]
    ]
    return {
        "site_id": site_id,
        "display_name": m["display_name"],
        "region_type": m["region_type"],
        "campus_role": m["campus_role"],
        "digital_divide_context": m["digital_divide_context"],
        "access_barriers": m["access_barriers"],
        "affordability_barriers": m["affordability_barriers"],
        "device_barriers": m["device_barriers"],
        "skills_barriers": m["skills_barriers"],
        "trust_privacy_barriers": m["trust_privacy_barriers"],
        "power_energy_barriers": m["power_energy_barriers"],
        "resilience_barriers": m["resilience_barriers"],
        "language_accessibility_barriers": m["language_accessibility_barriers"],
        "local_governance": m["local_governance"],
        "required_local_steering_circle_roles": m["steering_roles"],
        "local_partner_types_needed": m["partner_types"],
        "community_data_rights": "Community retains rights to aggregated insights; no raw PII in public repo",
        "no_foreign_savior_guardrails": m["guardrails"],
        "anchor_use_cases": [_anchor_uc(a) for a in m["anchors"]],
        "resilience_use_cases": [_resilience_uc(r) for r in m["resilience"]],
        "bad_day_scenarios": bad_day_scenarios,
        "metrics_definitions": metrics,
        "local_capacity_indicators": ["trainer_count_proxy", "mentor_hours_proxy", "open_lab_hours_proxy"],
        "evidence_to_collect": evidence,
        "source_assumptions": sources,
    }


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def campus_edge_profile(site_id: str, profile: dict) -> dict:
    crisis = site_id == "gaza"
    polar = site_id == "graham_land"
    gdpr = site_id == "germany"
    return {
        "site_id": site_id,
        "allowed_measurements": ["latency_ms", "jitter_ms", "packet_loss_pct", "throughput_mbps_stub"],
        "prohibited_measurements": ["precise_gps", "contact_list", "message_content", "biometrics"],
        "consent_mode": "explicit_opt_in",
        "privacy_tier": "aggregate_only" if crisis or polar else "tier_b_aggregate",
        "local_data_governance_notes": profile.get("local_governance", ""),
        "expected_device_classes": ["shared_tablet", "community_kiosk", "lab_handset"],
        "low_bandwidth_mode": True,
        "offline_first_mode": crisis or polar,
        "crisis_mode_restrictions": {
            "no_location_tracking": crisis,
            "no_person_identifiers": True,
            "remote_first_only": crisis,
        } if crisis else {},
        "retention_policy": "minimum_necessary_30d_stub",
        "export_target_7gc": f"results/campus_measurements/{site_id}_7gc_export.json",
        "gdpr_aware": gdpr,
        "accessibility_checks": site_id == "geelong",
    }


def campus_ntn_scenario(site_id: str) -> dict:
    names = {
        "gary": "gary_outage_learning_cache",
        "ghana": "ghana_power_backhaul_failure",
        "guyana": "guyana_flood_disaster_fallback",
        "gaza": "gaza_blackout_resilient_content",
        "geelong": "geelong_emergency_digital_services",
        "graham_land": "graham_land_satellite_window",
        "germany": "germany_rural_outage_fallback",
    }
    sid = names[site_id]
    return {
        "scenario_id": sid,
        "site_id": site_id,
        "service_context": f"{site_id} campus resilience",
        "normal_day_assumptions": {"terrestrial_up": True, "ntn_available": True},
        "bad_day_assumptions": {"terrestrial_up": False, "ntn_degraded": True},
        "worst_day_assumptions": {"terrestrial_up": False, "ntn_limited": True},
        "recovery_day_assumptions": {"terrestrial_restoring": True},
        "terrestrial_network_state": "configurable",
        "ntn_fallback_option": "leo_stub",
        "offline_cache_option": True,
        "priority_classes": ["emergency", "education", "general"],
        "local_risk_constraints": ["no_pii", "aggregate_metrics_only"],
        "metrics": ["service_continuity", "recovery_time_proxy", "priority_preservation"],
        "source_assumptions": [{"claim": "Link budget stub", "needs_local_validation": True}],
        "needs_validation": True,
    }


def main():
    profiles = {s: build_site_profile(s) for s in SITES}
    # 7gc site profiles
    twin = SPINE / "7gc-digital-twin" / "configs" / "site_profiles"
    for s, p in profiles.items():
        write_yaml(twin / f"{s}.yaml", p)
    # edge-io
    edge_dir = SPINE / "edge-io-measurement-node" / "configs" / "campus_measurement_profiles"
    for s, p in profiles.items():
        write_yaml(edge_dir / f"{s}.yaml", campus_edge_profile(s, p))
    # ntn
    ntn_dir = SPINE / "ntn-resilience-sim" / "configs" / "campus_scenarios"
    for s in SITES:
        write_yaml(ntn_dir / f"{campus_ntn_scenario(s)['scenario_id']}.yaml", campus_ntn_scenario(s))
    # waike tracks
    waike_dir = SPINE / "waike-research-ops" / "configs" / "campus_learning_tracks"
    for s, p in profiles.items():
        write_yaml(waike_dir / f"{s}.yaml", {
            "site_id": s,
            "local_context": p["campus_role"],
            "beginner_pathway": {"steps": ["run smoke test", "read problem map"], "repos": p["anchor_use_cases"][0]["repos_involved"]},
            "intermediate_pathway": {"steps": ["fix docs/tests", "export artifact"], "repos": REPOS_INVOLVED[:4]},
            "advanced_pathway": {"steps": ["close evidence issue", "reproduction log"], "repos": REPOS_INVOLVED},
            "local_capstone": f"{s} capstone: campus operational demo",
            "family_community_activity": f"{s} family learning night (template)",
            "instructor_role": "local instructor owns pacing",
            "local_mentor_role": "mentor reviews ethics",
            "gunnchai3k_support_mode": "tutor_cards",
            "portfolio_artifact": f"results/campus_learning/{s}_portfolio.md",
            "ethical_caution": "No PII; no savior narrative",
            "data_privacy_caution": "Aggregate exports only",
            "repo_issues_to_contribute": ["[Evidence TODO] items"],
            "evidence_of_learning": ["rubric", "reproduction note"],
        })
    # device-os modes
    dos_dir = SPINE / "gunnchos-device-os" / "configs" / "campus_device_modes"
    for s, p in profiles.items():
        write_yaml(dos_dir / f"{s}.yaml", {
            "site_id": s,
            "default_mode": "school" if s in ("gary", "geelong") else "research",
            "low_bandwidth_behavior": {"reduce_sync": True, "compress_exports": True},
            "offline_content_behavior": {"cache_lessons": True},
            "telemetry_policy": "opt_in_aggregate",
            "accessibility_settings": {"high_contrast": s == "geelong"},
            "crisis_privacy_restrictions": {"no_location": s == "gaza"},
            "school_fleet_policy": "fleet-v0-stub",
            "gunnchai3k_behavior": "guided_tutor",
            "waike_lesson_behavior": "track_from_yaml",
            "edge_io_behavior": "campus_profile",
            "seven_gc_export_behavior": "sanitized_json",
        })
    # hardware kits
    hw_dir = SPINE / "gunnchos-hardware-industrial-design" / "configs" / "campus_device_kits"
    for s in SITES:
        write_yaml(hw_dir / f"{s}.yaml", {
            "site_id": s,
            "kit_name": f"{s} campus kit",
            "device_mix": ["community_tablet", "lab_sbc", "rugged_router_stub"],
            "community_baseline_tier": "affordable_repairable",
            "research_lab_tier": "sensor_radio_dev",
            "frontier_prototype_tier": "mmwave_devkit_stub",
            "power_assumptions": "solar+battery where noted in site profile",
            "repair_assumptions": "modular parts list",
            "connectivity_assumptions": "wifi6e_stepping_stone",
            "accessibility_assumptions": "a11y_peripherals_for_geelong" if s == "geelong" else "standard",
            "privacy_security_assumptions": "tpm_target",
            "logistics_risks": ["import_delay", "parts_moq"],
            "local_maintenance_plan": "train local repair mentors",
            "evidence_needed_before_adoption": ["pilot_safety_review", "bom_quotes", "thermal_stub"],
            "manufacturing_ready": False,
        })
    # spectrumx airan
    sx_dir = SPINE / "spectrumx-ai-ran-gary" / "configs" / "campus_ai_ran_profiles"
    for s in SITES:
        write_yaml(sx_dir / f"{s}.yaml", {
            "site_id": s,
            "traffic_classes": ["education", "general", "emergency"],
            "fairness_priorities": ["neighborhood_equity_stub"],
            "low_bandwidth_constraints": True,
            "power_constraints": s in ("ghana", "graham_land"),
            "resilience_priority": s in ("gaza", "guyana", "graham_land"),
            "privacy_safety_constraints": ["no_pii"],
            "scenario_source_7gc": f"configs/site_profiles/{s}.yaml",
            "evidence_status": "smoke_test_only",
        })
    # readygary radio
    rg_dir = SPINE / "readygary-6g-beam-selection" / "configs" / "campus_radio_profiles"
    for s in SITES:
        write_yaml(rg_dir / f"{s}.yaml", {
            "site_id": s,
            "mobility_case": "pedestrian_stub",
            "blockage_case": "urban_nlos_stub",
            "latency_sensitivity": "high" if s == "gary" else "medium",
            "device_class": "handset_stub",
            "radio_environment_assumption": "configurable_channel_stub",
            "evidence_needed": ["realistic_channel_dataset", "hardware_latency"],
            "link_7gc_site_profile": f"7gc-digital-twin/configs/site_profiles/{s}.yaml",
            "evidence_status": "smoke_test_only",
        })
    ORCH.mkdir(parents=True, exist_ok=True)
    (ORCH / "MASTER_SOURCE_ASSUMPTIONS_REGISTER.md").write_text(
        "# Source assumptions\n\nGenerated from site profiles. All items marked needs_local_validation where applicable.\n",
        encoding="utf-8",
    )
    print("Generated campus YAML for all repos")


if __name__ == "__main__":
    main()
