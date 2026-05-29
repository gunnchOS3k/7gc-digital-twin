"""Scenario composition for multi-site runs."""
from .sites import load_site
from .synthetic_users import generate_users


def load_scenario(site_id: str) -> dict:
    site = load_site(site_id)
    n = int(site.get("population", {}).get("synthetic_users", 100))
    return {"site": site, "users": generate_users(n)}
