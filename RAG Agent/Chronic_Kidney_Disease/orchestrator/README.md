# Orchestrator (v2 — partner integration)

Plan-act loop integrating SQL agent + patient vector DB + partner's literature RAG
+ partner's recommendation generator. Output is markdown text (3 treatment options
with patient-grounded reasoning + citations) following the partner's `_call_llm` schema.

## Architecture

```
Orchestrator(subject_id, t_cutoff)
├── plan-act loop (max N turns)
│   each turn the LLM (our GPT-4o via Kong) picks ONE action:
│     - query_patient(q)     → BOTH sql_agent and patient vector_db; both saved
│     - query_literature(q)  → partner's BGE retrieval, top-k passages
│     - finalize             → break loop
├── step 1: our LLM extracts STRUCTURED PATIENT SUMMARY from transcript
│           (verbatim labs/meds with units, current medications, comorbidities)
└── step 2: partner's _call_llm produces the RECOMMENDATION
            inputs: question = patient_summary + clinical question
                    context  = concatenated literature blocks from transcript
            output: markdown with 3 ranked treatments, citations, fallback logic
```

## Why this design

- The partner's `generate.py` already has a heavily-tuned system prompt for
  literature-grounded clinical reasoning (mandatory verbatim value quoting, 3-option
  fallback, [Title (parent_block_id)] citation). We don't duplicate it.
- We control patient context gathering (multi-turn SQL+vector); partner controls
  the final answer formatting.
- Both retrieval traces (SQL rows AND vector chunks) are kept side-by-side in every
  patient_query turn, so downstream comparison is trivial.

## Environment expectations

- `sql_agent` package at `/gpfs/data/razavianlab/capstone/2025_agentic/sql_agent`
- `retrieve_ehr` at `/gpfs/data/razavianlab/capstone/2025_agentic/agentic_workflow`
- patient vector stores at `Chronic_Kidney_Disease/patient_db/subject_<sid>/`
- partner literature RAG at `agentic_rag_kk5739/` (override with `LIT_RAG_PATH`)
- partner exposes `generate._call_llm` and (optionally) `papers.jsonl` for titles
- cohort at `Chronic_Kidney_Disease/cohort_nodes.csv`

## Run

```bash
cd /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease

# one subject
/gpfs/scratch/zh1461/conda_envs/hf_env/bin/python -m orchestrator.run --subject-id 19421240

# all 8 subjects
/gpfs/scratch/zh1461/conda_envs/hf_env/bin/python -m orchestrator.run --all

# tune
/gpfs/scratch/zh1461/conda_envs/hf_env/bin/python -m orchestrator.run \
    --subject-id 12407578 --max-turns 6 --k-patient 5 --k-lit 5
```

## Output

Each run writes `orchestrator/runs/<UTC-timestamp>_subject_<sid>.json`:

```json
{
  "subject_id": "...",
  "t_cutoff":   "...",
  "stage":      "...",
  "duration_sec": 120.4,
  "n_turns_used": 5,
  "transcript": [
    {"turn": 0, "type": "patient_query",   "query": "...",
     "sql_agent": {...}, "vector_db": [...]},
    {"turn": 3, "type": "literature_query","query": "...", "literature": [...]}
  ],
  "patient_summary": "Patient context:\n- Demographics: ...\n- Recent labs:\n  ...",
  "recommendation":  "<markdown text from partner's _call_llm>\n\n1. ...\n2. ...\n3. ...\n\n### References\n..."
}
```

## File layout

| File | Purpose |
|---|---|
| `orchestrator.py` | Main `Orchestrator` class; plan-act loop; finalization |
| `lit_retrieval.py` | Caches BGE + vectors + titles; provides `retrieve_literature()` |
| `lit_generate.py` | Wraps partner's `_call_llm` for final recommendation |
| `prompts.py` | `PLAN_SYSTEM`, `SUMMARIZE_PATIENT` (our LLM only) |
| `run.py` | CLI |
| `runs/` | JSON transcripts |
