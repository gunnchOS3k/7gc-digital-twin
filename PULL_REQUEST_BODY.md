# Add PhD application readiness documentation

## Summary

This PR adds the PhD application readiness documentation suite for the 7GC digital-twin repository, establishing the scenario framework, evaluation methodology, and honest scoping for all seven nodes.

### What's included

- **PhD Application Readiness doc** — role, status, metrics, evidence, and explicit constraints on what is and is not claimed
- **7GC Scenario Framework** — framing the seven nodes as scenario classes for rigorous simulation-based evaluation, not as promised campus deployments
- **7 Scenario Cards** (Gary, Ghana, Guyana, Gaza, Geelong, Germany, Graham Land) — each documenting research purpose, connectivity stress case, digital-twin variables, ethics risks, and what is/is not claimed
- **GitHub Issues to Create** — 5 actionable next-step issues for simulation parameters, experiment scripts, ethics documentation, package implementation, and NTN integration
- **This PR body** — for reference

### What this does NOT claim

- Seven campuses will be built during the PhD
- Field access exists at any node
- Community partnerships are formalized
- Community data has been or will be collected without governance
- Digital twins prove real-world impact

### Methodology

All scenarios are designed as parameterized simulation environments. Gary is the primary proof context with the most development. Other nodes provide scenario diversity for evaluating 6G service-continuity architecture under varied connectivity stress conditions. Ethics-gated nodes (Gaza, Graham Land) exist only as simulation scenarios.

## Test Plan

- [ ] All markdown files render correctly on GitHub
- [ ] Scenario cards follow consistent format
- [ ] No claims of field access, partnerships, or community data
- [ ] Readiness doc accurately reflects current repository state
- [ ] Issues are actionable and scoped appropriately
