#!/bin/bash
#SBATCH --job-name=ckd_orch_test
#SBATCH --partition=cpu_short
#SBATCH --time=01:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --output=/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739/integration_test_runs/slurm_%j.out
#SBATCH --error=/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739/integration_test_runs/slurm_%j.err

set -euo pipefail

echo "host: $(hostname)"
echo "started: $(date)"

module load python/gpu/3.10.6
unset PGUSER

cd /gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739/integration_test_runs
/gpfs/scratch/kk5739/rag_venv/bin/python -u run_integration_test.py

echo "ended: $(date)"
