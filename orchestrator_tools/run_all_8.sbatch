#!/bin/bash
#SBATCH --job-name=ckd_all_8
#SBATCH --partition=cpu_short
#SBATCH --time=01:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --output=/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739/orchestrator_tools/all_8_%j.out
#SBATCH --error=/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739/orchestrator_tools/all_8_%j.err

set -uo pipefail
echo "host: $(hostname)"; echo "started: $(date)"

cd /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease

PY=/gpfs/scratch/zh1461/conda_envs/hf_env/bin/python

$PY -m orchestrator.run --subject-id 16468520
$PY -m orchestrator.run --subject-id 19421240
$PY -m orchestrator.run --subject-id 12407578
$PY -m orchestrator.run --subject-id 18992637
$PY -m orchestrator.run --subject-id 10043050
$PY -m orchestrator.run --subject-id 16237451
$PY -m orchestrator.run --subject-id 11234135
$PY -m orchestrator.run --subject-id 14991576

echo "ended: $(date)"
echo "--- new files in runs/ today ---"
ls -la /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator/runs/ \
    | grep "$(date +%Y%m%d | sed 's/^20//;s/^/2026/')" || \
ls -la /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator/runs/
