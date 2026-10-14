"""Generate markdown research cards from scenario summaries."""
from __future__ import annotations


def research_card(site_id: str, summary: dict, toy_metrics: dict) -> str:
    lines = [
        f"# Research Card — {site_id}",
        "",
        "## Purpose",
        "Community-scale digital twin toy scenario for supervisor/research demo.",
        "",
        "## Key metrics",
    ]
    for k, v in {**summary, **toy_metrics}.items():
        if k != "note":
            lines.append(f"- **{k}**: {v}")
    lines.extend(["", "## Limitation", toy_metrics.get("note", summary.get("note", "Research prototype only."))])
    return "\n".join(lines) + "\n"
