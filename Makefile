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
	python3 scripts/e2e_check_required_artifacts.py


# Smoke test only — not evidence of readiness
smoke: e2e
