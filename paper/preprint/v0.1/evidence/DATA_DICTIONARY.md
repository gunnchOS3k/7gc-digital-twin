# Paper I data and metric dictionary

| Item | Definition and unit | Interpretation boundary |
|---|---|---|
| Profile corpus | 21 stored snapshots: desk, mobile/docked, local-creation, wearable | Authored fixture states, not device measurements |
| `continuity_level_derived` | Ordered category: failed, minimum useful, degraded, target | Categories have no cardinal-utility spacing |
| Offline coverage | Boolean declared support for a workload | No executed application correctness test |
| Context overlay | 20 rows from five Gary names mapped to common snapshots | Lookup assumption, not community evidence |
| Seed | Independent seeded synthetic timeline with common configured priors | Experimental unit; n=30 |
| `task_completion_ratio` C | Mean gated synthetic successes per class-step; fraction | No jobs-per-second or measured task time |
| `time_above_minimum_useful` tau | Mean useful-state indicator; fraction | Abstract steps of unspecified duration |
| `reliability` | tau | Duplicate endpoint |
| outage/QoE/packet-loss proxy | 1-tau | Three duplicate complements; no packet/QoE campaign |
| throughput proxy | 5*tau, labeled Mbps by code | Arbitrary scalar transform |
| compute-completion-time proxy | 48*(1.2-0.4*C) | Synthetic transform; no wall-clock unit |
| `recovery_event_count` | Entries into outage episodes | Does not count successful recoveries |
| latency/jitter/energy | Authored stress/demand proxies | Uncalibrated; no radio, battery or human measurement |

Class fractions and seed aggregates are rounded to six decimals before reporting; display uses four decimals. Four stochastic classes differ from the four fixture profiles and must not be pooled as the same devices. Missing fixture cells mean untested combinations, not successes.
