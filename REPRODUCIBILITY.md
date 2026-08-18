# Reproducibility — 7GC Digital Twin (RQ1)

This repository produces **synthetic site profiles and benchmarks**. It does not produce RF campaign measurements, community-deployment evidence, or any University of Oulu affiliation claim.

Gary is the **flagship scenario**. Ghana, Guyana, Gaza, Geelong, Graham Land, and Germany are **scenario environments**, not community deployments.

## Clone / setup / run

```bash
git clone https://github.com/gunnchOS3k/7gc-digital-twin.git
cd 7gc-digital-twin
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
make test
make smoke   # long e2e; synthetic only
make reproduce
```

Canonical independent digital path: `make reproduce` → `scripts/reproduce.py` → `results/experiments/rq1_gary_flagship_profiles.json` and `results/reproduce/REPRODUCE_RECORD.json`.

## Expected outputs

- `pytest -q` passes on the synthetic path
- Gary experiment JSON includes workload / compute / radio / failure / mobility families labeled `synthetic_fixture`
- Provenance records repository commit and non-claims
- No claim of field deployment from these outputs

## Tool versions

| Tool | Version guidance |
|------|------------------|
| Python | 3.10+ |
| Make | GNU Make |
| pytest | from `requirements-dev.txt` |

Record exact versions in any independent reproduction log.

## Fresh machine checklist

- [ ] Clone repo and check out a frozen SHA
- [ ] Create a clean venv
- [ ] Run `make test`
- [ ] Run `make reproduce`
- [ ] Compare `output_hashes` in `results/reproduce/REPRODUCE_RECORD.json`
- [ ] Do not relabel synthetic radio stubs as measurements

## Evidence discipline

**Real today:** YAML schemas, synthetic fixtures, scene builder, metric families, provenance stamps, tests.

**Synthetic / demo-only:** `sinr_db_stub`, energy stubs, GeoJSON anchors, conference tables.

**Planned:** open-data-backed scenes and consented Edge-IO ingest.

**Not claimed:** operational city digital twin; community deployment of non-Gary 7GC names; Oulu affiliation.
