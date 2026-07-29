# Gates 4–6 Soft Adapter Contract (7gc-digital-twin)

This document describes **optional soft fields** that the Oulu research repo
(`gunnchos-emergent-service-intent-protocols`) may consume from this twin
repository. There are **no hard dependencies**: missing siblings or missing
fields must not break imports or CI in either repo.

## Non-goals

- No required Python import of Oulu code from this repo
- No required package pin across repos
- No physical Gate 6 evidence created by adapter docs alone

## Soft adapter fields (twin → Oulu)

| Field | Type | Meaning |
|---|---|---|
| `site_id` | string | Campus / site key (`gary`, `ghana`, …) |
| `twin_state_path` | string \| null | Path to exported twin state JSON if present |
| `scene_mode` | string | e.g. `synthetic-fixture`, `open-data` |
| `rf_geometry_ref` | string \| null | Optional RF geometry artifact reference |
| `evidence_label` | string | Taxonomy label; default `SYNTHETIC_EXPERIMENT` for fixtures |
| `adapter_status` | string | `AVAILABLE` \| `MISSING_SIBLING` \| `STUB` |

## Soft adapter fields (Oulu → twin, optional)

| Field | Type | Meaning |
|---|---|---|
| `service_intent_id` | string \| null | Intent id if an Oulu run produced one |
| `intent_priority` | number \| null | Optional priority hint |
| `constraints` | string[] | Soft constraint tags (`forbid_ntn`, …) |
| `comm_mode` | string \| null | Oulu communication mode label |

## Integration rule

Oulu adapters should `try` sibling discovery under `../7gc-digital-twin` and
fall back to stubs when absent. This repo remains independently runnable.
