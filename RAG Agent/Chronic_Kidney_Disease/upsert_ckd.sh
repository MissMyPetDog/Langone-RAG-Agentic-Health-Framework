#!/bin/bash
#SBATCH --job-name=upsert_ckd
#SBATCH --output=/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/upsert_ckd_%j.log
#SBATCH --error=/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/upsert_ckd_%j.err
#SBATCH --gres=gpu:a100:1
#SBATCH --partition=a100_short
#SBATCH --time=03:00:00

PYTHON=/gpfs/scratch/zh1461/conda_envs/hf_env/bin/python

echo "=== CKD upsert job started at $(date) ==="
echo "Host: $(hostname)"
nvidia-smi | head -20

export CUDA_VISIBLE_DEVICES=0

cd /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/
$PYTHON upsert_ckd.py

echo "=== CKD upsert done at $(date) ==="
