"""Synthetic user population generator (no PII)."""
import random


def generate_users(n: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    return [
        {"user_idx": i, "demand_mbps": rng.uniform(1, 50), "mobility": rng.choice(["static", "pedestrian"])}
        for i in range(n)
    ]
