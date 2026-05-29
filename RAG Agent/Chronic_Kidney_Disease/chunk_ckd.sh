#!/bin/bash
#SBATCH --job-name=chunk_ckd
#SBATCH --output=/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/chunk_ckd_%j.log
#SBATCH --error=/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/chunk_ckd_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --partition=cpu_short

PYTHON=/gpfs/scratch/zh1461/conda_envs/hf_env/bin/python

echo "=== CKD chunking job started at $(date) ==="
echo "Host: $(hostname)"

cd /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/
$PYTHON build_ckd_chunks.py

echo "=== CKD chunking done at $(date) ==="
