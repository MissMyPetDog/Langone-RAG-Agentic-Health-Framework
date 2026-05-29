# Agentic RAG Workflow — CKD Treatment Planning

An agentic Retrieval-Augmented-Generation system that produces literature-grounded,
patient-specific treatment recommendations for **Chronic Kidney Disease (CKD)**
patients. It combines a natural-language SQL agent, two patient-specific vector
stores, and a downstream clinical-literature RAG, coordinated by a plan-act
orchestrator.

> **Data policy.** This repository contains **code only**. All MIMIC-IV / PHI data,
> vector stores, schema metadata, run transcripts, and logs are excluded via
> `.gitignore` (see [Excluded artifacts](#excluded-artifacts-must-be-provided-locally)).
> MIMIC-IV is credentialed PhysioNet data and must never be committed.

---

## 1. What data is this built on?

- **Source:** [MIMIC-IV](https://physionet.org/content/mimiciv/) (schemas
  `mimiciv_hosp`, `mimiciv_icu`, `mimiciv_ed`) served from a PostgreSQL instance,
  plus MIMIC-IV discharge notes.
- **Cohort:** a CKD cohort defined in `cohort_nodes.csv`, one row per case with
  `subject_id`, `node_admittime`, and `stage` (CKD unspecified, ESRD, and stages
  1 / 2 / 3a / 3b / 4 / 5). The bundled sample covers 8 cases (one per stage).
- **Time cutoff (`t_cutoff`).** Each case has a decision-point timestamp
  (`node_admittime`). Every retrieval path is filtered to data **strictly before
  `t_cutoff`**, simulating the information a clinician would have had at that
  moment and preventing label leakage. The patient vector store is built only
  from pre-cutoff rows; discharge notes are restricted to admissions that had
  already been admitted **and** discharged before `t_cutoff`.

---

## 2. The databases / stores

| # | Store | What it holds | Built by | Queried by |
|---|---|---|---|---|
| 1 | **PostgreSQL (MIMIC-IV)** | Full structured records (`hosp`/`icu`/`ed`) | external (MIMIC load) | `sql_agent` (NL → SQL) |
| 2 | **Patient vector DB** | Per-patient serialized rows, pre-`t_cutoff`, embedded with `BAAI/bge-m3` → `patient_db/subject_<sid>/` | `build_patient_dbs.py` | `retrieve_ehr.py` (cosine / MMR) |
| 3 | **Discharge-notes DB** | Chunked discharge notes (Chroma), `BAAI/bge-m3`, collection `ckd_8_notes_bge` → `NotesDB/ckd_8_db/` | `build_ckd_chunks.py` → `upsert_ckd.py` | Chroma query, filtered by `subject_id` |
| 4 | **Literature RAG (downstream)** | BGE-embedded clinical-literature corpus | the **`momo`** branch (`agentic_rag_kk5739`) | `lit_retrieval.py` / `lit_generate.py` via `LIT_RAG_PATH` |

Stores 2 and 3 are patient-derived and are **not** committed; build them locally
with the scripts above. Store 4 lives on the `momo` branch and is wired in at
runtime (see [Integration](#integration-with-the-downstream-literature-rag)).

---

## 3. How the orchestrator interacts

`Orchestrator(subject_id, t_cutoff, stage)` runs a **plan-act loop** (`orchestrator/orchestrator.py`).
Each turn our planner LLM (NYU Kong GPT-4o) sees the full transcript so far and
picks exactly one action:

- **`query_patient(q)`** — runs **three retrieval paths in parallel**, all scoped
  to this patient and `t_cutoff`, and stores all three side-by-side:
  1. `sql_agent` — NL → PostgreSQL over the structured records (precise facts:
     labs, ICD codes, medication entries),
  2. patient `vector_db` — semantic search over serialized patient rows,
  3. `notes` — semantic search over this patient's prior discharge notes
     (narrative context: provider reasoning, plans, hospital course).
- **`query_literature(q)`** — top-k passages from the downstream literature RAG.
- **`finalize`** — exit the loop.

When the loop finalizes, a **two-step synthesis** runs:

1. our LLM extracts a **structured patient summary** from the transcript
   (verbatim labs/meds with units, comorbidities, narrative context);
2. the downstream `generate._call_llm` produces the **recommendation** — three
   ranked treatment options with patient-grounded rationale and literature
   citations — using its own tuned system prompt (we do not override it).

Each run is written to `orchestrator/runs/<UTC-timestamp>_subject_<sid>.json`
(transcript + patient summary + recommendation). **These transcripts contain
patient data and are git-ignored.**

```
Orchestrator(subject_id, t_cutoff, stage)
├── plan-act loop (max_turns)
│     query_patient → [sql_agent | patient vector_db | discharge notes]
│     query_literature → downstream literature RAG
│     finalize
├── step 1: our LLM → structured patient summary
└── step 2: downstream _call_llm → ranked, cited recommendation
```

---

## 4. Running the orchestrator

Once you have a **case number** (`subject_id`), a reachable **PostgreSQL server**
with MIMIC-IV loaded, and connection parameters set, you can run the orchestrator
directly.

### 4.1 Configure connections

Set credentials via environment variables (preferred) or in `sql_agent/config.py`:

| Variable | Meaning |
|---|---|
| `MIMIC_DB_HOST` / `MIMIC_DB_PORT` | PostgreSQL host / port |
| `PGUSER` | DB user |
| `MIMIC_DB_NAME` | database name |
| `KONG_API_KEY` | NYU Kong GPT-4o API key |
| `LIT_RAG_PATH` | path to the downstream literature RAG checkout (`momo` branch) |

You also need the local artifacts listed in [Excluded artifacts](#excluded-artifacts-must-be-provided-locally)
(patient stores, notes DB, `metadata.yaml`, `cohort_nodes.csv`).

### 4.2 Install

```bash
pip install -r sql_agent/requirements.txt
```

### 4.3 Run

```bash
cd "RAG Agent/Chronic_Kidney_Disease"

# one case
python -m orchestrator.run --subject-id <SUBJECT_ID>

# all cases in cohort_nodes.csv
python -m orchestrator.run --all

# tune the loop / retrieval depth
python -m orchestrator.run --subject-id <SUBJECT_ID> --max-turns 8 --k-patient 5 --k-lit 5
```

`run.py` reads `t_cutoff` and `stage` for the case from `cohort_nodes.csv`, so you
only pass the `subject_id`.

---

## Integration with the downstream literature RAG

The literature retrieval and recommendation generation live on the **`momo`**
branch (`agentic_rag_kk5739`: `retrieval.py`, `generate.py`, `papers.jsonl`).
This branch does **not** vendor or modify that code. Instead, check out `momo`
into a separate location and point the orchestrator at it:

```bash
export LIT_RAG_PATH=/path/to/agentic_rag_kk5739
```

`lit_retrieval.py` and `lit_generate.py` import the downstream modules from
`LIT_RAG_PATH` at runtime.

---

## Repository layout

```
RAG Agent/
├── sql_agent/                  # NL → PostgreSQL agent (SELECT-only, self-correcting)
│   ├── agent.py  cli.py  config.py  db.py  llm.py  schema.py  validator.py
│   ├── metadata.yaml           # MIMIC table descriptions  (LOCAL ONLY — git-ignored)
│   └── tests/
└── Chronic_Kidney_Disease/
    ├── build_patient_dbs.py    # build per-patient vector store (pre-t_cutoff)
    ├── build_ckd_chunks.py     # chunk discharge notes (pre-t_cutoff)
    ├── upsert_ckd.py           # upsert note chunks into Chroma
    ├── extract_ground_truth.py
    ├── viewer.py
    └── orchestrator/
        ├── orchestrator.py     # plan-act loop + 2-step finalization
        ├── run.py              # CLI
        ├── retrieve_ehr.py     # patient vector store retrieval (cosine / MMR)
        ├── lit_retrieval.py    # downstream literature retrieval wrapper
        ├── lit_generate.py     # downstream recommendation wrapper
        └── prompts.py
```

---

## Excluded artifacts (must be provided locally)

The following are git-ignored and must be supplied in your local checkout — they
are either credentialed MIMIC-IV data, patient-derived, or large:

- `ckd_samples/`, `lookup_tables/` — MIMIC-IV raw samples and dictionary tables
- `patient_db/`, `NotesDB/` — patient/notes vector stores
- `cohort_nodes.csv`, `*_chunks.jsonl` — cohort and derived chunks
- `sql_agent/metadata.yaml` — schema/table-description metadata
- `runs/`, `logs/`, `*.log`, `*.err` — run transcripts and logs (contain patient data)
