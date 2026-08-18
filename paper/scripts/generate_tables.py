#!/usr/bin/env python3
"""Generate Paper I tables/figures from experiment JSON. Never invent missing numbers."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "results" / "experiments" / "rq1_gary_flagship_profiles.json"
TABLES = ROOT / "paper" / "tables"
FIGURES = ROOT / "paper" / "figures"
ARTIFACTS = ROOT / "paper" / "artifacts"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)

LEVELS = ["target", "degraded", "min_useful", "failed"]
CLASSES = ["desk", "mobile-docked", "local-creation", "wearable"]


def _tex(s: object) -> str:
    return str(s).replace("_", "\\_").replace("%", "\\%")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print("wrote", path)


def _pending(reason: str) -> None:
    body = (
        "% RESULT_PENDING — run `make paper-reproduce` before citing numbers.\n"
        f"\\textbf{{RESULT\\_PENDING.}} {reason}\\par\n"
    )
    for name in (
        "rq1_runs.tex",
        "rq1_continuity_levels.tex",
        "rq1_failure_cases.tex",
        "rq1_gary_overlay.tex",
        "rq1_seed_sensitivity.tex",
        "rq1_site_inclusion.tex",
        "rq1_findings.tex",
    ):
        _write(TABLES / name, body)


def _table(caption: str, header: str, body: str, spec: str) -> str:
    return (
        "\\begin{table}[h]\n\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\begin{{tabular}}{{{spec}}}\\toprule\n"
        f"{header} \\\\\\midrule\n"
        f"{body}\n"
        "\\bottomrule\\end{tabular}\n\\end{table}\n"
    )


def _svg_heatmap(path: Path, row_labels: list[str], col_labels: list[str], values: list[list[float]], title: str) -> None:
    cell = 48
    left = 140
    top = 48
    width = left + cell * len(col_labels) + 24
    height = top + cell * len(row_labels) + 40
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'<text x="12" y="20" font-size="12">{title}</text>',
    ]
    for j, lab in enumerate(col_labels):
        parts.append(
            f'<text x="{left + j * cell + cell / 2}" y="{top - 8}" font-size="9" text-anchor="middle">{lab}</text>'
        )
    for i, lab in enumerate(row_labels):
        parts.append(f'<text x="8" y="{top + i * cell + cell / 2 + 4}" font-size="10">{lab}</text>')
        for j, val in enumerate(values[i]):
            # 0 failed (dark), 1 min_useful, 2 degraded, 3 target (light)
            t = max(0.0, min(1.0, val / 3.0))
            r = int(220 - 140 * (1 - t))
            g = int(80 + 140 * t)
            b = int(90 + 40 * t)
            x = left + j * cell
            y = top + i * cell
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" fill="rgb({r},{g},{b})" stroke="#333"/>'
            )
            parts.append(
                f'<text x="{x + cell / 2}" y="{y + cell / 2 + 3}" font-size="9" text-anchor="middle" fill="#111">{val:.0f}</text>'
            )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("wrote", path)


def _try_png(path: Path, row_labels: list[str], col_labels: list[str], values: list[list[float]], title: str) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; SVG/CSV only for", path.name)
        return
    fig, ax = plt.subplots(figsize=(7, 3.6))
    im = ax.imshow(values, cmap="RdYlGn", vmin=0, vmax=3, aspect="auto")
    ax.set_xticks(range(len(col_labels)), col_labels, rotation=30, ha="right")
    ax.set_yticks(range(len(row_labels)), row_labels)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3], label="0 failed … 3 target")
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            ax.text(j, i, f"{values[i][j]:.0f}", ha="center", va="center", color="black", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print("wrote", path)


def main() -> int:
    if not SRC.exists():
        _pending("Experiment JSON not present.")
        return 0
    data = json.loads(SRC.read_text(encoding="utf-8"))
    cont = data.get("continuity_benchmark") or {}
    panel = data.get("site_metric_panel") or {}
    findings = data.get("findings") or {}
    sha = str(data.get("result_sha256") or "")[:16]

    run_rows = []
    for run in data.get("runs") or []:
        run_rows.append(
            f"{run.get('seed')} & {run.get('mean_demand_mbps')} & {run.get('p95_demand_mbps')} & "
            f"{run.get('jains_fairness_on_demand')} & {_tex(run.get('radio_evidence_status'))} \\\\"
        )
    _write(
        TABLES / "rq1_runs.tex",
        _table(
            "RQ1 Gary synthetic-user demand by seed (SYNTHETIC\\_SIM; not RF).",
            "seed & mean demand (Mbps) & p95 demand (Mbps) & Jain fairness & radio evidence",
            "\n".join(run_rows) or "\\multicolumn{5}{c}{RESULT\\_PENDING} \\\\",
            "rcccc",
        )
        + f"% sha {sha}\n",
    )

    counts = cont.get("level_counts_by_class") or {}
    level_rows = []
    for cls in CLASSES:
        c = counts.get(cls) or {}
        level_rows.append(
            f"{_tex(cls)} & {c.get('target', 0)} & {c.get('degraded', 0)} & "
            f"{c.get('min_useful', 0)} & {c.get('failed', 0)} \\\\"
        )
    _write(
        TABLES / "rq1_continuity_levels.tex",
        _table(
            "Continuity-level counts by device class on the frozen Device OS injected corpus "
            "(SYNTHETIC\\_SIM).",
            "class & target & degraded & min-useful & failed",
            "\n".join(level_rows),
            "lcccc",
        ),
    )

    failed = cont.get("failed_cases") or []
    if failed:
        fail_body = "\n".join(
            f"{_tex(r.get('research_class'))} & {_tex(r.get('workload'))} & "
            f"{_tex(r.get('scenario_id'))} & {_tex(r.get('active_bearer'))} & "
            f"{_tex(r.get('continuity_level_derived'))} \\\\"
            for r in failed
        )
    else:
        fail_body = "\\multicolumn{5}{c}{no failed cases in corpus} \\\\"
    _write(
        TABLES / "rq1_failure_cases.tex",
        _table(
            "Cases below min-useful (failed). Empty would mean no class dropped below min-useful "
            "in this digital corpus.",
            "class & workload & scenario & bearer & level",
            fail_body,
            "lllll",
        ),
    )

    overlay = cont.get("gary_overlay") or []
    ov_body = "\n".join(
        f"{_tex(r.get('gary_scenario_id'))} & {_tex(r.get('mapped_bearer_stress'))} & "
        f"{_tex(r.get('research_class'))} & {_tex(r.get('workload'))} & "
        f"{_tex(r.get('continuity_level'))} \\\\"
        for r in overlay
    ) or "\\multicolumn{5}{c}{RESULT\\_PENDING} \\\\"
    _write(
        TABLES / "rq1_gary_overlay.tex",
        _table(
            "Gary bad-day names mapped to frozen bearer-stress labels (mapping is a protocol "
            "assumption, not a field measurement).",
            "Gary scenario & mapped stress & class & workload & continuity",
            ov_body,
            "lllll",
        ),
    )

    seed_body = "\n".join(
        f"{r.get('seed')} & {r.get('mean_demand_mbps')} & {r.get('p95_demand_mbps')} & "
        f"{r.get('pedestrian_fraction')} \\\\"
        for r in (panel.get("gary_seed_runs") or [])
    ) or "\\multicolumn{4}{c}{RESULT\\_PENDING} \\\\"
    _write(
        TABLES / "rq1_seed_sensitivity.tex",
        _table(
            "Gary synthetic-user sensitivity across pre-registered seeds (SYNTHETIC\\_SIM).",
            "seed & mean demand (Mbps) & p95 demand (Mbps) & pedestrian fraction",
            seed_body,
            "rccc",
        ),
    )

    site_body = "\n".join(
        f"{_tex(r.get('site_id'))} & {r.get('is_flagship')} & {r.get('digital_inclusion_readiness')} & "
        f"{r.get('access_barrier_score')} & {r.get('mean_demand_mbps')} \\\\"
        for r in (panel.get("site_inclusion") or [])
    ) or "\\multicolumn{5}{c}{RESULT\\_PENDING} \\\\"
    _write(
        TABLES / "rq1_site_inclusion.tex",
        _table(
            "Comparative scenario-environment inclusion families (not community deployments).",
            "site & flagship & inclusion readiness & access barrier & mean demand (Mbps)",
            site_body,
            "lcccc",
        ),
    )

    failed_desc = ", ".join(
        f"{r.get('research_class')}/{r.get('workload')}/{r.get('scenario_id')}" for r in failed
    ) or "none"
    findings_tex = (
        "The frozen Device OS corpus contains "
        f"{int(cont.get('n_scenarios') or 0)} class--scenario rows. "
        f"Re-derived continuity levels matched stored labels: "
        f"{str(findings.get('level_rederive_all_match')).lower()}. "
        f"Classes that reached \\texttt{{failed}} (below min-useful): "
        f"{_tex(findings.get('classes_that_failed') or [])}. "
        f"Classes that never failed: {_tex(findings.get('classes_never_failed') or [])}. "
        f"Failed cases: {_tex(failed_desc)}. "
        f"Labeled \\texttt{{degraded\\_wifi}} rows that remained \\texttt{{target}}: "
        f"{findings.get('degraded_wifi_n_still_target')}. "
        f"Gary overlay rows below min-useful: {findings.get('gary_overlay_n_below_min_useful')}. "
        f"Gary mean demand across seeds ranged "
        f"{findings.get('gary_mean_demand_mbps_min')}--"
        f"{findings.get('gary_mean_demand_mbps_max')}~Mbps "
        f"(range {findings.get('gary_mean_demand_mbps_range')}). "
        "All numbers are \\texttt{SYNTHETIC\\_SIM}.\n"
    )
    _write(TABLES / "rq1_findings.tex", findings_tex)

    # Heatmap: class x scenario using derived level order.
    scenarios = []
    for r in cont.get("scenario_rows") or []:
        if r.get("scenario_id") not in scenarios:
            scenarios.append(r["scenario_id"])
    lookup = {(r["research_class"], r["scenario_id"]): r for r in (cont.get("scenario_rows") or [])}
    shared = [sid for sid in scenarios if all((cls, sid) in lookup for cls in CLASSES)]
    level_map = {"failed": 0, "min_useful": 1, "degraded": 2, "target": 3}
    grid = []
    for cls in CLASSES:
        grid.append(
            [float(level_map.get((lookup[(cls, sid)] or {}).get("continuity_level_derived"), -1)) for sid in shared]
        )

    if shared and grid:
        csv_path = FIGURES / "rq1_continuity_heatmap.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["research_class", *shared])
            for cls, row in zip(CLASSES, grid):
                w.writerow([cls, *row])
        print("wrote", csv_path)
        _svg_heatmap(
            FIGURES / "rq1_continuity_heatmap.svg",
            CLASSES,
            shared,
            grid,
            "Continuity level (0 failed, 1 min-useful, 2 degraded, 3 target) SYNTHETIC_SIM",
        )
        _try_png(
            FIGURES / "rq1_continuity_heatmap.png",
            CLASSES,
            shared,
            grid,
            "RQ1 continuity levels (SYNTHETIC_SIM)",
        )

    slim = {
        "experiment_id": data.get("experiment_id"),
        "result_sha256": data.get("result_sha256"),
        "findings": findings,
        "failed_cases": failed,
        "level_counts_by_class": counts,
        "gary_seed_runs": panel.get("gary_seed_runs"),
        "evidence_status": "synthetic_fixture",
        "never": ["SUBMITTED", "ACCEPTED"],
    }
    slim_path = ARTIFACTS / "rq1_experiment_summary.json"
    slim_path.write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
    print("wrote", slim_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
