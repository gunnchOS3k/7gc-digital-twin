# Claims to evidence (Paper I)

Root matrix: [../CLAIMS_TO_EVIDENCE.md](../CLAIMS_TO_EVIDENCE.md) and [../quality/CLAIMS_TO_EVIDENCE_MATRIX.md](../quality/CLAIMS_TO_EVIDENCE_MATRIX.md).

| Claim | Allowed | Evidence |
|---|---|---|
| Synthetic Gary profiles run with seeds 1,2,7,42 | yes | `rq1_gary_flagship_profiles` JSON + `paper/tables/rq1_seed_sensitivity.tex` |
| Wearable × offline_coding is below min-useful when forced offline | yes, SYNTHETIC_SIM | `paper/tables/rq1_failure_cases.tex` |
| Desk / mobile-docked / local-creation never failed on the frozen corpus | yes, SYNTHETIC_SIM | `paper/tables/rq1_continuity_levels.tex` |
| Labeled `degraded_wifi` remains `target` in this corpus | yes, SYNTHETIC_SIM | findings JSON `degraded_wifi_n_still_target` |
| RF channel sounding | no | MEASUREMENT_PENDING |
| Community deployment | no | scenario environment flag |
| Oulu affiliation | no | non-claim in provenance |
| SUBMITTED / ACCEPTED | no | `MANUSCRIPT_STATUS.md` |
