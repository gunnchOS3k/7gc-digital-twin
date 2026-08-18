# Claims to evidence — 7gc-digital-twin

Thesis: Resilience-Aware Service Continuity in Heterogeneous 6G Networks. This repo answers **RQ1 (profiles/benchmarks)** digitally.

| Claim | Evidence level | Artifact | Status |
|-------|----------------|----------|--------|
| Python CLI runs site validation and synthetic scenes | 1 smoke / unit | `make test`, `make smoke` | PASS on CI path |
| Gary is flagship; other 7GC names are scenario environments | 2 documented config | `configs/sites/*.yaml`, `tests/test_rq1_supervisor_digital.py` | PASS digital |
| Workload / compute / radio / failure / mobility families exist | 2 synthetic metrics | `src/seven_gc_twin/campus_metrics.py` | PASS; radio is stub |
| Experiment manifest is reproducible | 2 synthetic experiment | `configs/experiments/rq1_gary_flagship_profiles.yaml`, `make reproduce` | PASS digital |
| Independent second-person reproduction | pending | `docs/packets/EXTERNAL_REPRODUCTION_PACKET.md` | PENDING |
| RF campaign / channel sounding | not claimed | — | NOT CLAIMED |
| Community deployment of Ghana/Guyana/Gaza/Geelong/Graham Land/Germany | not claimed | `scenario_environment_not_community_deployment` | NOT CLAIMED |
| University of Oulu affiliation | not claimed | README / provenance non-claims | NOT CLAIMED |
| Field-calibrated twin | planned | future UML | OPEN |
