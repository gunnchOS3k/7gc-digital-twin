# 7gc-digital-twin

Community-scale **AI-RAN + digital twin** research scaffold (Gary flagship + comparative scenario nodes).

> **Current release/state:** `DIGITALLY_VALIDATED` research twin — **NOT the gunnchOS3k product spine**. Portal + field-kit charter are canonical.

Ecosystem portal: [gunnchos-research-portal](https://github.com/gunnchOS3k/gunnchos-research-portal) · Product charter: [gunnchOS3k_PRODUCT_CHARTER.md](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/blob/main/program/charter/gunnchOS3k_PRODUCT_CHARTER.md)

## What is this?

Site-aware simulation scaffold, metrics (fairness, spectral/energy, latency, NTN hooks), and lab/testbed integration contracts.

## Why does it exist?

Compare connectivity policies *before* deployment for under-connected communities — research, not operations.

## Where does it fit?

Product Charter **layer 10** (twin research). Linked from portal as research — **not** control-plane / product spine.

## What is real today?

- Site schemas, CLI/Streamlit smoke paths, `make smoke` / `make e2e`
- Metrics library and scene builders as documented
- Contracts toward Edge-IO / AI-RAN / NTN research repos

## What is simulated / modelled?

- Synthetic campus/community scenes and policy comparisons
- Optional Sionna/DeepMIMO/aerial tooling paths when enabled — still research

## What is physical / external pending?

- Field-calibrated twin correlation
- Any operational carrier network claim — **not claimed**
- Reinstating this repo as product spine — **rejected**

## Try / inspect in 5 minutes

```bash
pip install -r requirements.txt
make test
make smoke   # synthetic only
```

## Architecture

Python twin + `configs/` sites + `apps/` demos + metrics → `results/e2e/`.

## Repo map

| Path | Role |
|---|---|
| `configs/` | Sites/scenarios |
| package/apps | Twin + demos |
| `quality/` | Claims/evidence |
| `docs/history/` | Prior spine claim (HISTORICAL) |

## Interfaces

Research contracts with spectrumx, edge-io, ntn-resilience-sim. Does **not** own Product Charter.

## Tests

```bash
make lint test contract-test validate-sites
```

## Evidence

`results/e2e/` synthetic summaries. Not digital-equality field proof.

## Known gaps

Calibration to real measurements; non-spine navigation clarity in older forks/mirrors.

## Beginner path

A **flight simulator** for community internet plans — not the airport authority (that’s portal + charter).

## Intern path

Run smoke; open one site config; list synthetic assumptions.

## Expert path

Scene builders + metrics without spine/6G commercial overclaim.

## Contribution path

Twin fidelity + honesty. Point newcomers to the Ecosystem Portal.

## Current release / state

**DIGITALLY_VALIDATED**. Claim boundary: `not_canonical_product_spine`.

## Claim boundary

NOT product spine · no commercial 6G · no certification · Cursor DRAFT-only.

---

## Retained detail (post–Cycle 3A front door)

Prior spine claim note: [docs/history/PRIOR_SPINE_CLAIM.md](docs/history/PRIOR_SPINE_CLAIM.md).

Full prior README: [docs/history/README_PRE_WP012.md](docs/history/README_PRE_WP012.md).

Retained entrypoints: [docs/START_HERE.md](docs/START_HERE.md) · [docs/HOW_THIS_FITS_GUNNCHOS.md](docs/HOW_THIS_FITS_GUNNCHOS.md).
