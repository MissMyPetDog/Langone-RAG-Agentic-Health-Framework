#!/usr/bin/env bash
# Create .venv and install deps. CPU PyTorch is installed first (smaller than CUDA
# wheels + nvidia-* packages — avoids OOM "Killed" on low-RAM login nodes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d "$ROOT/.venv" ]]; then
  python3 -m venv "$ROOT/.venv"
fi
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

pip install -U pip wheel setuptools

# Must run before `pip install -r requirements.txt` so sentence-transformers
# does not pull default (CUDA) torch from PyPI.
pip install torch --index-url https://download.pytorch.org/whl/cpu

pip install -r "$ROOT/requirements.txt"

echo "Done. Activate with: source $ROOT/.venv/bin/activate"
