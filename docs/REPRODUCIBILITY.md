# Reproducibility

## Quickstart

```bash
git clone https://github.com/gunnchOS3k/7gc-digital-twin.git
cd 7gc-digital-twin
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m seven_gc_twin.cli summarize gary
```

## Tests

```bash
pytest -q
```

## Sample data policy

Synthetic/toy only. **No private competition data.** No student PII.

## Regenerate artifacts

Demo commands write to `results/` or `docs/generated/` where applicable.

## Citation

See `CITATION.cff` in repo root.
