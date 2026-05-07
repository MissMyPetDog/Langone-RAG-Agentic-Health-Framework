"""End-to-end integration smoke test for the orchestrator.

Runs the partner's Orchestrator for each CKD stage/subject and saves the
resulting transcripts into THIS user's workspace (since the orchestrator's own
runs/ directory is not writable by us).

Why this script exists:
    The default `python -m orchestrator.run --subject-id ...` writes to
    /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator/runs
    which is owned by user `zh1461`. As `kk5739` we cannot write there, so we
    monkey-patch `orchestrator.orchestrator.RUNS_DIR` before instantiating
    Orchestrator.

Usage:
    module load python/gpu/3.10.6
    /gpfs/scratch/kk5739/rag_venv/bin/python run_integration_test.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent

if "PGUSER" in os.environ:
    del os.environ["PGUSER"]

CKD_PROJECT = Path("/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease")
if str(CKD_PROJECT) not in sys.path:
    sys.path.insert(0, str(CKD_PROJECT))

from orchestrator import orchestrator as orch_mod
from orchestrator.orchestrator import Orchestrator

orch_mod.RUNS_DIR = THIS_DIR
orch_mod.RUNS_DIR.mkdir(parents=True, exist_ok=True)

SUBJECTS = [
    ("CKD, unspecified", "16468520", "2140-10-17 02:13:00"),
    ("ESRD",             "19421240", "2180-07-12 18:26:00"),
    ("Stage 1",          "12407578", "2121-04-27 12:57:00"),
    ("Stage 2",          "18992637", "2173-03-24 13:23:00"),
    ("Stage 3_a",        "10043050", "2169-04-01 23:13:00"),
    ("Stage 3b",         "16237451", "2117-05-21 07:36:00"),
    ("Stage 4",          "11234135", "2176-11-02 17:55:00"),
    ("Stage 5",          "14991576", "2142-07-20 10:18:00"),
]

MAX_TURNS = 8
K_PATIENT = 5
K_LIT = 5


def run_one(stage: str, sid: str, t_cutoff: str) -> dict:
    print(f"\n{'#'*70}\n# {stage}  subject_id={sid}\n{'#'*70}")
    t0 = time.time()
    try:
        orch = Orchestrator(
            subject_id=sid,
            t_cutoff=t_cutoff,
            stage=stage,
            max_turns=MAX_TURNS,
            k_patient_vector=K_PATIENT,
            k_literature=K_LIT,
        )
        result = orch.run(save=True)
    except Exception as e:
        traceback.print_exc()
        return {
            "stage": stage,
            "subject_id": sid,
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "duration_sec": round(time.time() - t0, 1),
        }

    rec = result.get("recommendation", "") or ""
    summ = result.get("patient_summary", "") or ""
    transcript = result.get("transcript", []) or []
    n_pat = sum(1 for t in transcript if t.get("type") == "patient_query")
    n_lit = sum(1 for t in transcript if t.get("type") == "literature_query")

    rec_ok = bool(rec) and not rec.startswith("ERROR")
    summ_ok = bool(summ) and not summ.startswith("ERROR")

    print(f"\n--- patient summary ({len(summ)} chars) ---\n{summ[:500]}")
    print(f"\n--- recommendation ({len(rec)} chars) ---\n{rec[:1000]}")

    return {
        "stage": stage,
        "subject_id": sid,
        "ok": rec_ok and summ_ok,
        "n_turns": result.get("n_turns_used"),
        "n_patient_queries": n_pat,
        "n_lit_queries": n_lit,
        "summary_chars": len(summ),
        "recommendation_chars": len(rec),
        "duration_sec": result.get("duration_sec"),
    }


def main():
    summary = []
    grand_t0 = time.time()
    for stage, sid, tcut in SUBJECTS:
        summary.append(run_one(stage, sid, tcut))
    grand_dur = round(time.time() - grand_t0, 1)

    print("\n\n" + "=" * 80)
    print(f"INTEGRATION TEST RESULTS  (total {grand_dur}s)")
    print("=" * 80)
    header = (
        f"{'stage':<20}{'subject_id':<14}{'ok':<5}{'turns':<7}"
        f"{'pat_q':<7}{'lit_q':<7}{'summ':<8}{'rec':<8}{'sec':<7}"
    )
    print(header)
    print("-" * len(header))
    n_ok = 0
    for s in summary:
        if s.get("ok"):
            n_ok += 1
            print(f"{s['stage']:<20}{s['subject_id']:<14}{'OK':<5}"
                  f"{str(s.get('n_turns','-')):<7}{str(s.get('n_patient_queries','-')):<7}"
                  f"{str(s.get('n_lit_queries','-')):<7}"
                  f"{str(s.get('summary_chars','-')):<8}"
                  f"{str(s.get('recommendation_chars','-')):<8}"
                  f"{str(s.get('duration_sec','-')):<7}")
        else:
            print(f"{s['stage']:<20}{s['subject_id']:<14}{'FAIL':<5}"
                  f"  err={s.get('error','?')}  dur={s.get('duration_sec','-')}s")
    print("-" * len(header))
    print(f"{n_ok}/{len(summary)} subjects produced a valid summary + recommendation")

    summary_path = THIS_DIR / "integration_test_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nSaved summary to {summary_path}")


if __name__ == "__main__":
    main()
