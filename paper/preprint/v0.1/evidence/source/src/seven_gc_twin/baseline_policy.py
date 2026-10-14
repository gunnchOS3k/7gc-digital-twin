"""Baseline resource allocation policy stub."""


def proportional_fair(allocations: list[float], demand: list[float]) -> list[float]:
    if not allocations:
        return []
    total = sum(demand) or 1.0
    return [a * (d / total) for a, d in zip(allocations, demand)]
