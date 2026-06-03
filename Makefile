.PHONY: test demo e2e

PY := PYTHONPATH=src

test:
	$(PY) pytest -q

demo:
	$(PY) python3 -m seven_gc_twin.cli summarize gary

e2e:
	@mkdir -p results/e2e results/site_profiles
	python3 scripts/bootstrap_site_profiles.py 2>/dev/null || true
	$(PY) pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli list-sites >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli run-all-sites --mode smoke >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli make-campus-report gary >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli integration-map gary >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli summarize gary
	$(PY) python3 -m seven_gc_twin.cli export gary --format json
	$(PY) python3 -m seven_gc_twin.cli metrics gary --toy
	$(PY) python3 -m seven_gc_twin.cli make-report gary
	python3 scripts/e2e_postprocess.py
	python3 scripts/run_all_tool_exports.py 2>> results/e2e/e2e_terminal_output.txt || true
	$(MAKE) e2e-tooling 2>> results/e2e/e2e_terminal_output.txt || true
	python3 scripts/e2e_check_required_artifacts.py


# Smoke test only — not evidence of readiness
smoke: e2e


e2e-tooling:
	@mkdir -p results/tool_exports
	python3 scripts/run_all_tool_exports.py 2>/dev/null || python3 scripts/check_optional_backends.py || true

e2e-sionna e2e-deepmimo e2e-aerial e2e-oran:
	@echo "Optional target $@ — requires external install; not run in default CI"
