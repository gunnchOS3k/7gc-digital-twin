# Paper I reproducibility supplement

Experimental source: `1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa` in gunnchOS3k/7gc-digital-twin. Recovered publication HEAD: `632cbbb0c91ae59617806b2a9e2313916231521f`. Publication commits do not redefine this frozen experimental source. Seeds are integers 1..30; each seed contains 48 abstract steps for each of four stochastic classes. No seconds conversion or population sampling is implied.

Create a Python 3.12 environment and install `reproduction/requirements-lock.txt`. From the repository root:

```sh
PYTHONPATH=src python -m pytest -q tests/test_rq1_statistical_parity.py tests/test_rq1_supervisor_digital.py tests/test_site_profiles_operational.py
PYTHONPATH=src python paper/submission/scripts/verify_current.py
python paper/scripts/build_owner_review.py
python paper/scripts/package_submission.py
```

The current focused suite passes 27 tests. Fresh execution matches the scientific payload exactly, with variable provenance and paths separately validated. Source/config/protocol hashes, independent Student-t calculations, original reproduction record and fresh output are retained in reproduction/. The deterministic 21-row profile classifier and stochastic generator are separate paths. No source/config edits or seed substitutions were made.

Python version used for this continuation is 3.12.14, NumPy 2.3.5 and SciPy 1.18.1. The generator uses Python `random.Random`; class order, short-circuit task draws and rounding must remain unchanged. Statistical intervals are over 30 seed means, with df=29. Endpoint differences from independent SciPy recomputation are below 1e-10. They measure generator variability, not real-world uncertainty.

Compile the synchronized package from paper/submission with pdfLaTeX, then BibTeX, then pdfLaTeX twice, using `-no-shell-escape -halt-on-error -interaction=nonstopmode`. TinyTeX was used here. Official IEEE Access assets are unchanged; the manuscript preamble suppresses invented publication metadata. All output pages must be visually inspected after substantive edits. Editable sources and figure descriptions provide alternative reading material; the manuscript PDF is not asserted to be tagged PDF/UA.

## Repaired verifier v2

current_verification.json is the actual successful record. The comparison retains stable provenance semantics; excludes only root output locations, root result_sha256 and producer commit/generated_at/content_sha256 inside typed provenance stamps. Every stamp hash and the whole-result hash are recomputed; producer repository, resolvable Git commit and timezone-bearing timestamp are checked. All original and fresh provenance is retained. Scientific content digests are never broadly excluded. Fresh v2 outputs are in fresh_verifier_v2; historical records remain unchanged. `python paper/submission/scripts/test_verify_current.py` passes four tests, including deliberate scientific alteration with a recomputed valid hash and invalid provenance rejection. Output paths are checked as nonempty locations, not portability or file existence promises for historical machines.
