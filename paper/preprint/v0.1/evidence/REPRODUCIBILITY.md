# Paper I v0.1 reproducibility

The evidence archive is bounded to the frozen Git source snapshot, necessary configs/fixtures/contracts, retained outputs, audit/plot scripts, dependency records, hashes and notices. No large external literature PDF, Git history, credentials, machine environment or IEEE template is redistributed. Exact revisions are in PROVENANCE.json; every retained frozen file maps to its Git-byte checksum in evidence/source/MANIFEST.json. Full experimental SHA is 1a5491bf9261f77a75cc0fa7edbb5f25b425c7aa. The paper-development and preprint-source revisions are distinct. Archives are associated with that source anchor; final packaging commits are recorded outside the archive to avoid a self-referential SHA.

## Clean source build

Extract paper-i-v0.1-source.zip into an empty directory, verify SHA256SUMS before running anything, then:

```sh
python3 VERIFY_MANIFEST.py
sh BUILD.sh
```

Requires standard TeX Live with pdfLaTeX, BibTeX, article, geometry, fontenc, lmodern, amsmath/amssymb/amsfonts, graphicx, booktabs, array, url, natbib, hyperref and plainnat. No shell escape, IEEE class, logo, publisher style, absolute include path or bundled third-party template. Install the distribution yourself if absent; BUILD.sh assumes commands are available on PATH. PDF binary metadata may differ across builds; the accepted clean rebuild was checked page-by-page by pixel hash.

## Clean evidence execution

Extract paper-i-v0.1-evidence.zip into a separate empty directory and set your working directory there. Use the recorded Python/dependency environment if available; otherwise create an environment and install the pinned lock. The accepted test reused an existing Python3.14.7 environment on macOS; it was not a fresh OS or cross-platform dependency installation.

```sh
python3 scripts/verify_manifest.py
# Optional environment setup; a new install was not the acceptance test:
python3 -m venv .venv
.venv/bin/python -m pip install -r environment/acceptance-requirements.txt
# Use that Python, or an existing equivalent environment:
python3 scripts/reproduce.py
python3 scripts/independent_audit.py
python3 scripts/test_verifier.py
python3 scripts/verify_claims.py
python3 scripts/generate_figures.py
```

For a newly created .venv, replace python3 in the execution lines with .venv/bin/python. Historical source/requirements.txt is retained unchanged but covers other repository UI functions and is not the minimal audit lock. PyYAML and jsonschema support the frozen source; SciPy provides t/quad; NumPy/Matplotlib support plotting. No large new sweep or more seeds is required. The archived snapshot and original outputs stay fixed. Fresh runtime outputs go to generated/; original retained output records remain in reproduction/.

The fresh result must match the historical scientific payload SHA f8d15b0297088611b065f28ef2c65e1cb1aba86641adfd9da6ddb640e3c47772, 21 corpus rows and all 30×4 generator rows. Primary means/SD/intervals are reported in SCIENTIFIC_REVIEW.md. Original report contains all per-seed outcomes; expected schema is documented in DATA_DICTIONARY.md. New volatile whole-result hash, output locations and producer metadata are retained in generated/current_verification.json, separately validated, and excluded from exact scientific comparison only as documented in VERIFIER_EXCLUSIONS.md.

A clean non-Git extraction legitimately generates producer.commit="unknown" through the unchanged historical stamp code. The portable wrapper checks revision syntax/known historical identities and retains unknown explicitly; it does not fabricate a producer SHA or prove that an unknown runtime producer is a Git object. Exact frozen source bytes are verified against the archive/Git-derived manifest. In the original checkout, original_git_verifier.py additionally resolves producer Git objects. Historical stored absolute output locations are observational provenance, not required execution paths. The generated record explicitly sets git_metadata_available=false. Check the manifest before execution; generated files and Python caches are outside its retained payload scope.

Figure generation may update export timestamps, SVG IDs or PDF metadata; source data and displayed values are fixed. Verify original files before regenerating. New table numeric cells must match retained tables; neutral spacing differs deliberately. Use the release PDF/source archive for exact accepted rendering. There is no independent external human reproduction, physical measurement, calibration or novelty approval.
