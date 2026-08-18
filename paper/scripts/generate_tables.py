#!/usr/bin/env python3
"""Generate Paper I tables from experiment JSON. Never invent missing numbers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "results" / "experiments" / "rq1_gary_flagship_profiles.json"
OUT = ROOT / "paper" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
DEST = OUT / "rq1_runs.tex"


def main() -> int:
    if not SRC.exists():
        DEST.write_text(
            "% RESULT_PENDING — run `make paper-reproduce` before citing numbers.\n"
            "\\textbf{RESULT\\_PENDING.} Experiment JSON not present.\\par\n",
            encoding="utf-8",
        )
        print("wrote RESULT_PENDING", DEST)
        return 0
    data = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for run in data.get("runs") or []:
        seed = run.get("seed")
        ev = (run.get("campus_metrics") or {}).get("families", {}).get("radio", {}).get("evidence_status", "unknown")
        rows.append(f"{seed} & {ev} \\\\")
    body = "\n".join(rows) or "\\multicolumn{2}{c}{RESULT\\_PENDING} \\\\"
    DEST.write_text(
        "\\begin{table}[h]\n\\centering\n"
        "\\caption{RQ1 synthetic-fixture runs (not RF). evidence\\_status from campus metrics.}\n"
        "\\begin{tabular}{rl}\\toprule\nseed & radio evidence status \\\\\\midrule\n"
        f"{body}\n\\bottomrule\\end{{tabular}}\n"
        f"\\end{{table}}\n% sha {data.get('result_sha256','')[:16]}\n",
        encoding="utf-8",
    )
    print("wrote", DEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
