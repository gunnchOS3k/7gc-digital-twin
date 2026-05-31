# Runbook

```bash
pip install -r requirements.txt
pytest -q
PYTHONPATH=src python3 -m seven_gc_twin.cli summarize gary
```

Expected: exit 0, artifact under results/ or docs/generated/.
