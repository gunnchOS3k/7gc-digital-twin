# RQ1 statistical report (SYNTHETIC_SIM)

- scenario_family_id: `gary_flagship_continuity_profiles`
- seeds: `[1, 2, 7, 42]`
- n: 4
- CI method: student_t_over_seed_means @ 0.95
- evidence_class: `SYNTHETIC_SIM`

> 95% Student-t CIs quantify simulation-run variability across seeds, NOT real-world RF measurement uncertainty.

## Primary outcomes

| metric | n | mean | std | 95% CI low | 95% CI high |
|---|---:|---:|---:|---:|---:|
| task_completion_ratio | 4 | 0.441407 | 0.050384 | 0.361245 | 0.521568 |
| time_above_minimum_useful | 4 | 0.578125 | 0.062065 | 0.479380 | 0.676869 |

## Per-seed primary

| seed | task_completion_ratio | time_above_minimum_useful |
|---:|---:|---:|
| 1 | 0.369792 | 0.489583 |
| 2 | 0.479167 | 0.630208 |
| 7 | 0.473958 | 0.609375 |
| 42 | 0.442709 | 0.583333 |

