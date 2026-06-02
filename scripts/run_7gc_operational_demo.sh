#!/usr/bin/env bash
# Cross-repo operational demo (skips missing sibling repos gracefully)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPINE="$(cd "$ROOT/../.." && pwd)"
OUT="$ROOT/results/7gc_operational_demo"
mkdir -p "$OUT"

export PYTHONPATH="$ROOT/src"

echo "== 7gc-digital-twin campus reports =="
cd "$ROOT"
python3 -m seven_gc_twin.cli run-all-sites --mode smoke | tee "$OUT/7gc_run.log"

run_repo() {
  local name="$1"
  local cmd="$2"
  local dir="$SPINE/$name"
  if [ -d "$dir" ]; then
    echo "== $name =="
  (cd "$dir" && eval "$cmd") >> "$OUT/${name}.log" 2>&1 || echo "WARN: $name command failed"
  else
    echo "SKIP $name (not cloned at $dir)" >> "$OUT/${name}.log"
  fi
}

run_repo "edge-io-measurement-node" "PYTHONPATH=src python3 -m edge_io_node.cli run-all-campus --mode local-safe 2>/dev/null || PYTHONPATH=src python3 scripts/run_all_campus_measurements.py"
run_repo "ntn-resilience-sim" "PYTHONPATH=src python3 -m ntn_resilience.cli run-all-campus"
run_repo "waike-research-ops" "python3 scripts/generate_all_campus_tracks.py"
run_repo "gunnchos-device-os" "python3 scripts/generate_all_campus_mode_reports.py"
run_repo "gunnchos-hardware-industrial-design" "python3 scripts/generate_campus_device_kits.py"
run_repo "spectrumx-ai-ran-gary" "PYTHONPATH=src:src/airan_research python3 scripts/run_all_campus_airan.py"
run_repo "readygary-6g-beam-selection" "python3 scripts/run_all_campus_radio.py"

cat > "$OUT/README.md" <<'EOF'
# 7GC Operational Demo Outputs

Smoke-test campus artifacts. **Not field validation.**

See per-repo `results/campus_*` and `results/site_profiles/`.
EOF

echo "Done. Outputs in $OUT"
