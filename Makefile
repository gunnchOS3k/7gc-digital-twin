.PHONY: test demo e2e

PY := PYTHONPATH=src

test:
	$(PY) pytest -q

demo:
	$(PY) python3 -m seven_gc_twin.cli summarize gary

e2e:
	@mkdir -p results/e2e
	$(PY) pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli list-sites >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli summarize gary
	$(PY) python3 -m seven_gc_twin.cli export gary --format json
	$(PY) python3 -m seven_gc_twin.cli metrics gary --toy
	$(PY) python3 -m seven_gc_twin.cli make-report gary
	python3 scripts/e2e_postprocess.py
	python3 scripts/e2e_check_required_artifacts.py
