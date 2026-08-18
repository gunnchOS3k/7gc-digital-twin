# Reproducibility (Paper I)

Canonical: [../REPRODUCIBILITY.md](../REPRODUCIBILITY.md)

Frozen protocol: [artifacts/experiment_protocol.yaml](artifacts/experiment_protocol.yaml)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt matplotlib
make paper-reproduce
```

Outputs:
- `results/experiments/rq1_gary_flagship_profiles.json` (gitignored working copy)
- `paper/artifacts/rq1_experiment_summary.json` (committed extract)
- `paper/tables/rq1_*.tex` generated, not typed
- `paper/figures/rq1_continuity_heatmap.{png,svg,csv}`

Independent human reproduction remains PENDING. Digital reproduce of this packet is the `make paper-reproduce` path.
