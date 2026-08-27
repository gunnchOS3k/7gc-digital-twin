# Research artifact index — RQ1 statistical parity

| Field | Value |
|-------|-------|
| Repo | `7gc-digital-twin` |
| Accepted base SHA | `4cd70169b35a67937eac076caaa7905ffd47adeb` |
| Candidate SHA | `b8c84e465fc89e3e14915a1f30ff8491645f884a` |
| Branch | `research/rq1-statistical-parity-001` |
| Environment | `.venv` Python (local); CI target 3.11 |
| Exact command | `PYTHONPATH=src python -m seven_gc_twin.cli run-experiment rq1_gary_flagship_profiles` |
| Seeds | `[1, 2, 7, 42]` |
| Scenario family | `gary_flagship_continuity_profiles` |
| Input provenance | Frozen Device OS continuity fixtures + seeded synthetic campus metrics |
| Outputs | `paper/artifacts/rq1_statistical_report.{json,csv,md}` (+ local `results/experiments/` on reproduce) |
| Evidence class | `SYNTHETIC_SIM` |
| CI method | Student-t 95% over seed means |
| CI warning | CIs quantify simulation-run variability, NOT real-world RF uncertainty |
| Limitations | Synthetic seeded timelines; not Pixel RF QoS; not OTA |
| Negative results | Wearable offline_coding remains below min-useful in frozen corpus |
| Physical / external not performed | `PIXEL_RF_QOS=PHYSICAL_PENDING`, `INDEPENDENT_REPRODUCTION=EXTERNAL_PENDING` |
