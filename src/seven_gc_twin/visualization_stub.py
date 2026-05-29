"""Placeholder hooks for dashboards and notebooks."""


def site_summary_table(scenarios: list[dict]) -> list[dict]:
    return [
        {
            "site_id": s["site"]["site_id"],
            "users": len(s["users"]),
            "is_flagship": s["site"].get("is_flagship", False),
        }
        for s in scenarios
    ]
