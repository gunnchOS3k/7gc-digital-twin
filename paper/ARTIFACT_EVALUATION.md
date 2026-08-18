# Artifact evaluation (Paper I)

| Artifact | Command | Evidence |
|---|---|---|
| Experiment JSON | `make paper-reproduce` | SYNTHETIC_SIM |
| Tables | `python3 paper/scripts/generate_tables.py` | generated, not typed |
| Tests | `PYTHONPATH=src pytest -q tests/test_rq1_supervisor_digital.py` | digital |
| Independent packet | `docs/packets/EXTERNAL_REPRODUCTION_PACKET.md` | PENDING human |

No hidden RESULT_PENDING numbers in a final-looking PDF: `manuscript.tex` carries an explicit banner.
