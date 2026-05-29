"""CLI entry point.

Usage:
    python -m orchestrator.run --subject-id <SUBJECT_ID>
    python -m orchestrator.run --all
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from .orchestrator import Orchestrator

COHORT_CSV = Path(
    "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/cohort_nodes.csv"
)


def run_one(subject_id, t_cutoff, stage, max_turns, k_patient, k_lit):
    print(f"\n========== subject_id={subject_id} stage={stage} ==========")
    orch = Orchestrator(
        subject_id=subject_id,
        t_cutoff=t_cutoff,
        stage=stage,
        max_turns=max_turns,
        k_patient_vector=k_patient,
        k_literature=k_lit,
    )
    result = orch.run(save=True)

    print("\n" + "=" * 60)
    print("PATIENT SUMMARY")
    print("=" * 60)
    print(result["patient_summary"])

    print("\n" + "=" * 60)
    print("RECOMMENDATION (literature-grounded)")
    print("=" * 60)
    print(result["recommendation"])
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--subject-id", default=None)
    p.add_argument("--all", action="store_true")
    p.add_argument("--max-turns", type=int, default=10)
    p.add_argument("--k-patient", type=int, default=5)
    p.add_argument("--k-lit", type=int, default=5)
    args = p.parse_args()

    if not args.subject_id and not args.all:
        p.error("provide --subject-id or --all")

    cohort = pd.read_csv(COHORT_CSV)
    cohort["subject_id"] = cohort["subject_id"].astype(str)

    if args.subject_id:
        sid = str(args.subject_id)
        rows = cohort[cohort.subject_id == sid]
        if len(rows) == 0:
            print(f"ERROR: subject_id={sid} not in {COHORT_CSV}", file=sys.stderr)
            sys.exit(1)
        r = rows.iloc[0]
        run_one(sid, r["node_admittime"], r["stage"], args.max_turns, args.k_patient, args.k_lit)
    else:
        for _, r in cohort.iterrows():
            run_one(
                r["subject_id"], r["node_admittime"], r["stage"],
                args.max_turns, args.k_patient, args.k_lit,
            )


if __name__ == "__main__":
    main()
