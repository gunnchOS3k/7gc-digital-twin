.PHONY: test demo

test:
	PYTHONPATH=src pytest -q

demo:
	PYTHONPATH=src python3 -m seven_gc_twin.cli summarize gary
