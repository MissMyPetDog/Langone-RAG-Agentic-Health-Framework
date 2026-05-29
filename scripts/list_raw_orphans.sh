#!/usr/bin/env bash
# Run list_raw_orphans.py with project .venv when present and executable.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/list_raw_orphans.py"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  exec "$ROOT/.venv/bin/python" "$PY" "$@"
elif [[ -x "$ROOT/.venv/bin/python3" ]]; then
  exec "$ROOT/.venv/bin/python3" "$PY" "$@"
else
  echo "Note: no $ROOT/.venv/bin/python — using PATH python3" >&2
  exec python3 "$PY" "$@"
fi
