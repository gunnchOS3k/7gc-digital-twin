# 7GC Digital Twin — AI-RAN Research Scaffold

**Spine repo** for the gunnchOS3k MLV **7GC AI-RAN Digital Twin Program**.

> **Research prototype / simulation scaffold** — not a claim of deployed 6G infrastructure.

## Thesis

Community-scale **AI-RAN + digital twin + edge device testbeds** for under-connected, spectrum-constrained communities.

- **Gary** — flagship node (node 1)
- **Ghana, Guyana, Gaza, Geelong, Graham Land, Germany** — comparative scenario nodes for research and future partnerships

## What this repo is

- Reproducible site-aware simulation scaffold
- Metrics library (fairness, spectral/energy efficiency, latency, NTN resilience hooks)
- Future lab/testbed integration contracts

## What this repo is not

- Operational carrier 6G network
- Certified consumer hardware
- Production telemetry store with PII

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
streamlit run apps/streamlit_app.py
```

## Sibling repos

- [spectrumx-ai-ran-gary](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary) — Gary AI-RAN benchmark
- [readygary-6g-beam-selection](https://github.com/gunnchOS3k/readygary-6g-beam-selection) — beam selection
- [edge-io-measurement-node](https://github.com/gunnchOS3k/edge-io-measurement-node) — field endpoints
- [ntn-resilience-sim](https://github.com/gunnchOS3k/ntn-resilience-sim) — NTN resilience

## License

MIT — see LICENSE.
