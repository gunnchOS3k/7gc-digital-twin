"""Research metrics stubs for 7GC comparative studies."""


def jains_fairness(allocations: list[float]) -> float:
    if not allocations or sum(allocations) == 0:
        return 0.0
    s = sum(allocations)
    s2 = sum(x * x for x in allocations)
    n = len(allocations)
    return (s * s) / (n * s2) if s2 else 0.0


def spectral_efficiency_bps_hz(sinr_db: float) -> float:
    import math
    sinr = 10 ** (sinr_db / 10)
    return math.log2(1 + sinr)


def energy_per_bit_joules(power_w: float, throughput_bps: float) -> float:
    if throughput_bps <= 0:
        return float("inf")
    return power_w / throughput_bps
