.PHONY: install test lint validate-sites build-scenes build-scenes-offline full-scenes conference-artifacts diagrams demo e2e smoke clean-results e2e-tooling e2e-sionna e2e-deepmimo e2e-aerial e2e-oran generate-7gc-campus-twin

generate-7gc-campus-twin:
	$(PY) python3 scripts/generate_7gc_campus_twin_bundle.py

PY := PYTHONPATH=src

install:
	pip install -r requirements.txt

test:
	$(PY) pytest -q

lint:
	@echo "lint: optional ruff not required for CI"

validate-sites:
	@for s in gary ghana guyana gaza geelong graham_land germany; do \
	  $(PY) python3 -m seven_gc_twin.cli validate-site $$s || exit 1; \
	done

build-scenes:
	$(PY) python3 -m seven_gc_twin.cli build-all-scenes --mode synthetic-fixture

build-scenes-offline:
	$(PY) python3 -m seven_gc_twin.cli build-all-scenes --mode synthetic-fixture

full-scenes: build-scenes conference-artifacts diagrams
	$(PY) python3 -m seven_gc_twin.cli build-all-scenes --mode open-data || $(PY) python3 -m seven_gc_twin.cli build-all-scenes --mode synthetic-fixture

conference-artifacts:
	$(PY) python3 -m seven_gc_twin.cli make-conference-artifacts

diagrams:
	$(PY) python3 -c "from seven_gc_twin.diagrams.diagram_data_export import export; export()"

demo:
	$(PY) python3 -m seven_gc_twin.cli summarize gary

clean-results:
	rm -rf results/scenes results/conference results/cross_repo results/diagrams_data results/full_7gc_cross_repo_demo

e2e:
	@mkdir -p results/e2e results/site_profiles
	python3 scripts/bootstrap_site_profiles.py 2>/dev/null || true
	$(MAKE) validate-sites
	$(MAKE) build-scenes-offline
	$(MAKE) conference-artifacts
	$(MAKE) diagrams
	$(PY) pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli build-all-scenes --mode synthetic-fixture >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli make-conference-artifacts >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli list-sites >> results/e2e/e2e_terminal_output.txt
	$(PY) python3 -m seven_gc_twin.cli summarize gary
	$(PY) python3 -m seven_gc_twin.cli export gary --format json
	$(PY) python3 -m seven_gc_twin.cli metrics gary --toy
	$(PY) python3 -m seven_gc_twin.cli make-report gary
	python3 scripts/e2e_postprocess.py
	python3 scripts/run_all_tool_exports.py 2>> results/e2e/e2e_terminal_output.txt || true
	$(MAKE) e2e-tooling 2>> results/e2e/e2e_terminal_output.txt || true
	python3 scripts/e2e_check_full_scenes.py
	python3 scripts/e2e_check_required_artifacts.py

smoke: e2e

e2e-tooling:
	@mkdir -p results/tool_exports
	python3 scripts/run_all_tool_exports.py 2>/dev/null || python3 scripts/check_optional_backends.py || true

e2e-sionna e2e-deepmimo e2e-aerial e2e-oran:
	@echo "Optional target $@ — requires external install; not run in default CI"
