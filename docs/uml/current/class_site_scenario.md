# Class — site / scenario (current)

Derived from `configs/sites/*.yaml`, `configs/site_profiles/*.yaml`, and `config/schema.py`.

```mermaid
classDiagram
  class SiteYaml {
    +site_id
    +display_name
    +node_role
    +is_flagship
    +scenario_environment_not_community_deployment
    +spectrum
    +population
    +radio.sinr_db_stub
    +energy_constraints.power_w_stub
  }
  class SiteProfile {
    +anchor_use_cases
    +resilience_use_cases
    +bad_day_scenarios
    +metrics_definitions
    +source_assumptions
    +no_foreign_savior_guardrails
  }
  class SyntheticUser {
    +user_idx
    +demand_mbps
    +mobility
  }
  class ExperimentManifest {
    +experiment_id
    +research_question
    +site_id
    +seeds
    +metrics
    +non_claims
  }
  class CampusMetrics {
    +workload
    +compute
    +radio
    +failure
    +mobility
    +inclusion
    +provenance
  }
  SiteYaml --> SiteProfile : site_id
  SiteProfile --> ExperimentManifest
  SiteYaml --> SyntheticUser
  ExperimentManifest --> CampusMetrics
```

`radio.sinr_db_stub` is a planning stub. It is not a measured SINR.
