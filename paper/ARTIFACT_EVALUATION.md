# Artifact evaluation (Paper I)

| Artifact | Command | Evidence |
|---|---|---|
| Frozen protocol | `paper/artifacts/experiment_protocol.yaml` | pre-registered |
| Experiment JSON | `make paper-reproduce` | SYNTHETIC_SIM |
| Summary extract | `paper/artifacts/rq1_experiment_summary.json` | generated |
| Tables | `python3 paper/scripts/generate_tables.py` | generated, not typed |
| Figures | `paper/figures/rq1_continuity_heatmap.*` | generated |
| Tests | `PYTHONPATH=src pytest -q tests/test_rq1_supervisor_digital.py` | digital |
| Independent packet | `docs/packets/EXTERNAL_REPRODUCTION_PACKET.md` | PENDING human |

No hidden RESULT_PENDING numbers in a final-looking PDF: `manuscript.tex` carries an explicit banner. Never SUBMITTED/ACCEPTED.
