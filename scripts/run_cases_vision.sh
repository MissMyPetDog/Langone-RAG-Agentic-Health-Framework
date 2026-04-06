#!/usr/bin/env bash
# Run generate.py with --vision for CASE_01 .. CASE_N (default 20).
# Usage:
#   ./scripts/run_cases_vision.sh              # CASE_01 .. CASE_20
#   ./scripts/run_cases_vision.sh 5 12         # CASE_05 .. CASE_12
# Optional: export CASE_TEXT_DIR=/path/to/case_texts (default: tester_for_momo path below)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CASEDIR="${CASE_TEXT_DIR:-/gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts}"
FROM="${1:-1}"
TO="${2:-20}"

cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv/bin/python under $ROOT" >&2
  exit 1
fi

# Cluster: uncomment if libpython errors appear
# export LD_LIBRARY_PATH="/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}"

for n in $(seq "$FROM" "$TO"); do
  id=$(printf 'CASE_%02d' "$n")
  f="$CASEDIR/${id}.txt"
  if [[ ! -f "$f" ]]; then
    echo "skip (missing): $f" >&2
    continue
  fi
  echo "========== $id ==========" >&2
  .venv/bin/python generate.py --patient-data-file "$f" --vision
done

echo "Done cases $FROM..$TO" >&2
