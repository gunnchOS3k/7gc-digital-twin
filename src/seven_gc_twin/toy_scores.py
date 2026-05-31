"""Toy digital-equality and readiness scores (synthetic; not field measurements)."""
from __future__ import annotations


def coverage_equity_score(fairness: float, n_users: int) -> float:
    """Higher when Jain fairness is high and population is served."""
    scale = min(1.0, n_users / 1000.0)
    return round(min(1.0, fairness * 0.85 + scale * 0.15), 4)


def energy_pressure_score(power_w: float, demand_mbps: float) -> float:
    """0–1 where higher = more pressure (worse). Toy proxy."""
    if demand_mbps <= 0:
        return 0.0
    pressure = power_w / max(demand_mbps, 1.0)
    return round(min(1.0, pressure / 10.0), 4)


def backhaul_constraint_score(capacity_gbps: float, demand_mbps: float) -> float:
    """0–1 constraint severity."""
    need = demand_mbps / 1000.0
    if capacity_gbps <= 0:
        return 1.0
    return round(min(1.0, need / capacity_gbps), 4)


def latency_risk_score(latency_ms: float, threshold_ms: float = 50.0) -> float:
    return round(min(1.0, latency_ms / threshold_ms), 4)


def digital_equality_readiness(
    coverage_equity: float,
    energy_pressure: float,
    backhaul_constraint: float,
    latency_risk: float,
) -> float:
    """Composite readiness (toy). Lower risk scores improve readiness."""
    raw = coverage_equity * 0.4 + (1 - energy_pressure) * 0.2
    raw += (1 - backhaul_constraint) * 0.2 + (1 - latency_risk) * 0.2
    return round(max(0.0, min(1.0, raw)), 4)


def compute_toy_metric_bundle(site: dict, users: list[dict], fairness: float) -> dict:
    demands = [u.get("demand_mbps", 1.0) for u in users]
    total_demand = sum(demands)
    energy = site.get("energy_constraints", {})
    backhaul = site.get("backhaul_assumptions", {})
    qos = site.get("qos", {})
    power_w = energy.get("power_w_stub", 5.0)
    cap = backhaul.get("capacity_gbps_stub", 1.0)
    latency = qos.get("latency_ms_stub", 25.0)
    ce = coverage_equity_score(fairness, len(users))
    ep = energy_pressure_score(power_w, total_demand)
    bc = backhaul_constraint_score(cap, total_demand)
    lr = latency_risk_score(latency)
    readiness = digital_equality_readiness(ce, ep, bc, lr)
    return {
        "coverage_equity_score": ce,
        "energy_pressure_score": ep,
        "backhaul_constraint_score": bc,
        "latency_risk_score": lr,
        "digital_equality_readiness_score": readiness,
        "note": "toy synthetic scores — not calibrated field measurements",
    }
