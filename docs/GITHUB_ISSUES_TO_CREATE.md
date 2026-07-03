# GitHub Issues to Create

## Issue 1: Define simulation parameters for Gary digital-twin model

**Labels:** enhancement, gary, simulation

Formalize the quantified network model parameters for the Gary node digital twin. Include building coverage models, user density curves, device mix distributions, time-of-day load profiles, and event spike scenarios. Document parameter ranges and default values for reproducible experiments.

**Acceptance criteria:**
- Parameter specification document exists
- Default parameter set produces a baseline simulation run
- Parameters are configurable via YAML/JSON config files

---

## Issue 2: Create reproducible experiment scripts for scenario evaluation

**Labels:** enhancement, infrastructure

Build a set of reproducible experiment scripts that execute parameterized simulations across scenario cards. Scripts should accept scenario parameters, run simulations, and output structured results for comparison.

**Acceptance criteria:**
- Experiment runner accepts scenario card parameters
- Results are output in structured format (CSV/JSON)
- README documents how to reproduce any experiment

---

## Issue 3: Document ethical constraints and governance requirements

**Labels:** documentation, ethics

Create a formal ethics constraints document covering all seven nodes. Define what is permissible at each readiness level, what requires IRB/ethics review, and what is permanently ethics-gated without formal governance agreements.

**Acceptance criteria:**
- Ethics matrix covers all 7 nodes
- Clear escalation path for each ethics tier
- Gaza and Graham Land explicitly marked as simulation-only

---

## Issue 4: Implement scenario parameterization in seven_gc_twin package

**Labels:** enhancement, code

Add scenario parameterization support to the `seven_gc_twin` Python package. Each scenario card should map to a configurable parameter set that can be loaded, modified, and executed programmatically.

**Acceptance criteria:**
- Each node has a loadable parameter class/config
- Parameters validate against documented ranges
- Integration tests verify parameter loading for all 7 nodes

---

## Issue 5: Build NTN integration simulation for Guyana and Graham Land scenarios

**Labels:** enhancement, simulation, NTN

Implement NTN (Non-Terrestrial Network) simulation modules for satellite-dependent scenarios. Model LEO satellite pass windows, handover latency, store-and-forward behavior, and weather-dependent availability.

**Acceptance criteria:**
- Satellite pass visibility model produces realistic availability windows
- NTN handover latency is measurable in simulation
- Store-and-forward effectiveness can be evaluated
- Works for both Guyana (partial NTN) and Graham Land (NTN-only) scenarios
