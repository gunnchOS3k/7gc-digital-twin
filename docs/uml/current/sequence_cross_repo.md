# Sequence — cross-repository (current)

Contract-level flow. Sibling repos are not executed inside this process except as optional JSON ingest.

```mermaid
sequenceDiagram
  participant E as edge-io-measurement-node
  participant T as 7gc-digital-twin
  participant N as ntn-resilience-sim
  participant S as spectrumx-ai-ran-gary
  participant B as readygary-6g-beam-selection
  E->>T: optional gunnchos.edge_measurement_batch JSON
  T->>T: ingest-edge / build-twin-state (gate2)
  T->>N: twin_state bundle contract (file, not live RPC)
  N->>T: resilience_decision_bundle contract
  T->>S: site profile + scenario YAML (handoff docs)
  T->>B: scenario environment name (Gary flagship)
  Note over T: Other 7GC names remain scenario environments
```

If the field-kit schema sibling is absent, integration maps report `incompatible` rather than inventing a live link.
