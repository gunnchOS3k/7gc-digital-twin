"""Scenario composition for multi-site runs."""
from .sites import load_site
from .synthetic_users import generate_users


def load_scenario(site_id: str) -> dict:
    site = load_site(site_id)
    pop = site.get("population_assumptions") or site.get("population") or {}
    n = int(pop.get("synthetic_users", 100))
    return {"site": site, "users": generate_users(n)}
