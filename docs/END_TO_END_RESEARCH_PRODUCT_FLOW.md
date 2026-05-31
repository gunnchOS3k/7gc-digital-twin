# End-to-End Research Product Flow — 7gc-digital-twin

| Stage | Artifact | Proof |
|-------|----------|-------|
| Problem | Community-scale 6G digital twin evaluation across 7GC sites. | README, charter |
| Research question | How can researchers compare fairness, energy, and latency across synthetic community nodes? | docs/02_REQUIREMENTS.md |
| System model | docs/diagrams/*.mmd | docs/05_UML_MODELING.md |
| Inputs | configs/, synthetic generators | reproducibility/data_policy.md |
| Method | docs/06_METHODS_AND_METRICS.md | code under src/ or sim/ |
| Demo | `make e2e` | reproducibility/E2E_RUN_RECORD.md |
| Output | results/e2e/ | listed artifacts |
| Metrics | demo JSON/MD | results/e2e/* |
| Limitations | docs/09_LIMITATIONS_AND_NON_CLAIMS.md | claims audit |
| Extension | reproducibility/extension_guide.md | researcher guide |
| Paper | paper/outline.md | publication path |
| WAIKE | docs/14_WAIKE_INTEGRATION.md | programs/ |
