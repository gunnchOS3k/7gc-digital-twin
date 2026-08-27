# Research artifact index — RQ1 statistical parity

| Field | Value |
|-------|-------|
| Repo | `7gc-digital-twin` |
| Accepted base SHA | `4cd70169b35a67937eac076caaa7905ffd47adeb` |
| Branch | `research/rq1-statistical-parity-001` |
| Environment | `.venv` Python 3.11 Framework; CI target 3.11 |
| Exact command | `PYTHONPATH=src python -m seven_gc_twin.cli run-experiment rq1_gary_flagship_profiles` |
| Seeds | `[1..30]` (n=30, predeclared contiguous; no outcome-based selection) |
| Seed runtime | ~2.1 s full experiment on local M-series (trivial; n=30 retained) |
| Scenario family | `gary_flagship_continuity_profiles` |
| Input provenance | Frozen Device OS continuity fixtures + seeded synthetic campus metrics |
| Outputs | `paper/artifacts/rq1_statistical_report.{json,csv,md}` (+ local `results/experiments/` on reproduce) |
| Evidence class | `SYNTHETIC_SIM` |
| CI method | Student-t 95% over seed means; t-crit from SciPy 1.18.0 `t.ppf(0.975,df)` table (stdlib runtime) |
| CI warning | CIs quantify simulation-run variability, NOT real-world RF uncertainty |
| Paired effect size | `d_z = mean(pairwise_differences) / sd(pairwise_differences)` |
| Limitations | Synthetic seeded timelines; not Pixel RF QoS; not OTA |
| Negative results | Wearable offline_coding remains below min-useful in frozen corpus |
| Physical / external not performed | `PIXEL_RF_QOS=PHYSICAL_PENDING`, `MMWAVE_OTA=PHYSICAL_PENDING`, `INDEPENDENT_REPRODUCTION=EXTERNAL_PENDING`, `CERTIFICATION=NOT_RUN`, `CARRIER_ACCEPTANCE=NOT_RUN` |
