# Traceability matrix — 7gc-digital-twin

| Diagram element | Source path |
|-----------------|-------------|
| CLI use cases | `src/seven_gc_twin/cli.py` |
| Site YAML | `configs/sites/*.yaml`, `src/seven_gc_twin/sites.py` |
| Campus profiles | `configs/site_profiles/*.yaml`, `src/seven_gc_twin/site_profiles.py` |
| Schema | `src/seven_gc_twin/config/schema.py` |
| Metric families | `src/seven_gc_twin/campus_metrics.py` |
| Scene build | `src/seven_gc_twin/scene_builder.py` |
| Experiment manifest | `configs/experiments/*.yaml`, `src/seven_gc_twin/experiment_manifest.py` |
| Provenance | `src/seven_gc_twin/provenance.py` |
| Cross-repo maps | `src/seven_gc_twin/integrations/*.py` |
| Gate 2 ingest | `src/seven_gc_twin/gate2/edge_ingest.py` |
| Reproduce | `scripts/reproduce.py`, `Makefile` |
| Non-claim: not community deployment | `scenario_environment_not_community_deployment` on every site |
| Flagship | `configs/sites/gary.yaml` `is_flagship: true` |

[← UML README](README.md)
