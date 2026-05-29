.PHONY: test demo
test:
	pytest -q
demo:
	python -m seven_gc_twin.cli summarize gary
