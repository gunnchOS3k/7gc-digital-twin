#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPINE="$(cd "$ROOT/../.." && pwd)"
OUT="$ROOT/results/full_7gc_cross_repo_demo"
mkdir -p "$OUT"
export PYTHONPATH="$ROOT/src"

echo "== 7GC full scenes =="
cd "$ROOT"
make build-scenes-offline
make conference-artifacts
cp -r results/scenes "$OUT/" 2>/dev/null || true
cp -r results/conference "$OUT/" 2>/dev/null || true

run_repo() {
  local name="$1" cmd="$2"
  local dir="$SPINE/$name"
  if [ -d "$dir" ]; then
    echo "== $name ==" | tee -a "$OUT/run.log"
    (cd "$dir" && eval "$cmd") >> "$OUT/${name}.log" 2>&1 || echo "WARN $name" >> "$OUT/run.log"
  else
    echo "SKIP $name — clone: git clone https://github.com/gunnchOS3k/$name" >> "$OUT/run.log"
  fi
}

run_repo "edge-io-measurement-node" "PYTHONPATH=src python3 scripts/run_all_campus_measurements.py"
run_repo "ntn-resilience-sim" "PYTHONPATH=src python3 -m ntn_resilience.cli run-all-campus"
run_repo "waike-research-ops" "python3 scripts/generate_all_campus_tracks.py"
run_repo "gunnchos-device-os" "python3 scripts/generate_all_campus_mode_reports.py"
run_repo "gunnchos-hardware-industrial-design" "python3 scripts/generate_campus_device_kits.py"
run_repo "spectrumx-ai-ran-gary" "python3 scripts/run_all_campus_airan.py"
run_repo "readygary-6g-beam-selection" "python3 scripts/run_all_campus_radio.py"

echo "Done: $OUT"
