# Agentic RAG (Medical Literature)

End-to-end pipeline: collect literature from PubMed and top journals using patient/disease queries → parse PDFs, chunk, and link → build a text (BGE) + multimodal (tables/images, CLIP) vector DB → retrieve and generate answers.

> Korean documentation: [README.md](README.md)

**Team repository**: [MissMyPetDog/Langone-RAG-Agentic-Health-Framework](https://github.com/MissMyPetDog/Langone-RAG-Agentic-Health-Framework)

```bash
git clone git@github.com:MissMyPetDog/Langone-RAG-Agentic-Health-Framework.git
cd Langone-RAG-Agentic-Health-Framework
cp .env.example .env   # set KONG_API_KEY
bash scripts/install_venv.sh && source .venv/bin/activate
```

`data/` is not in git. Symlink from shared GPFS or rebuild via the **Quick start** pipeline.

---

## Directory layout

```text
agentic_rag_kk5739/
├── fetch.py                    # PubMed full-text fetch
├── parse.py                    # PDF → blocks.jsonl
├── fill_image_ocr.py           # Fill missing image OCR (before chunk)
├── chunk.py                    # blocks → chunks
├── link.py                     # Assign parent_block_id
├── embed.py                    # Hash embedding (demo)
├── real_embed.py               # BGE text embedding
├── multimodal_embed.py         # CLIP table/image embedding
├── prune_multimodal_vectors.py # Trim multimodal vectors
├── embed_multimodal_resume.sh  # Resume multimodal embed on CPU
├── retrieval.py                # Search + parent expansion
├── rerank.py                   # BGE + cross-encoder (experimental CLI)
├── generate.py                 # RAG + Kong LLM answer generation
├── query_generator.py          # LLM query generation for PubMed/RAG
├── schema.py                   # JSONL TypedDict definitions
├── vectordb.py                 # Hash vector demo search
├── requirements.txt
├── scripts/
│   ├── install_venv.sh         # venv + CPU torch install
│   ├── list_raw_orphans.py     # raw/ vs assets.jsonl mismatch
│   ├── list_raw_orphans.sh
│   ├── run_cases_vision.sh     # Batch CASE_01~N with --vision
│   └── reports/
│       ├── vision_two_way.py   # Vision vs Text-only A/B metrics
│       └── vision_three_way.py # Vision vs OCR-only vs Text-only
├── orchestrator_tools/
│   ├── build_papers_jsonl.py   # data/raw → papers.jsonl + assets.jsonl
│   └── run_all_8.sbatch        # SLURM batch for 8 CKD patients
├── orchestrator_runs/          # Symlink → team orchestrator/runs/
├── papers.jsonl                # doc_id → title (citations, metadata)
├── assets.jsonl                # doc_id → PDF path (parse input)
├── data/                       # Gitignored — build locally (see below)
├── outputs/                    # Gitignored — generate.py results
├── outputs_baseline_v1/        # Gitignored — initial baseline runs
├── reports/                    # Vision A/B analysis reports
└── logs/                       # Gitignored — run logs
```

---

## Current corpus (2026-05)

| doc_id | Title (short) | source |
|--------|---------------|--------|
| `gilbert_acc_weight_2025` | ACC 2025 Medical Weight Management | manual |
| `ndumele_aha_ckm_2023` | AHA CKM Presidential Advisory | manual |
| `ndumele_ckm_synopsis_2023` | AHA CKM Synopsis | manual |
| `nihms_1913084` | Life's Essential 8 (AHA) | pubmed_central |
| `pmid_23499048` | KDIGO 2012 AKI Guideline | pubmed |

**Data scale (recent build)**

| File | Rows |
|------|-----:|
| `blocks.jsonl` | 1,221 |
| `chunks.jsonl` / `linked_chunks.jsonl` | 2,386 |
| `real_vectors.jsonl` | 2,345 (text only) |
| `vectors_multimodal.jsonl` | 41 (table + image) |

After adding PDFs under `data/raw/` or fetching via `fetch.py`, refresh metadata with:

```bash
.venv/bin/python orchestrator_tools/build_papers_jsonl.py
```

---

## Quick start

```bash
# 1) Environment
bash scripts/install_venv.sh
source .venv/bin/activate
cp .env.example .env   # then fill in KONG_API_KEY
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}
export KONG_API_KEY=...

# 2) Manual PDF corpus (PDFs already in data/raw/)
.venv/bin/python orchestrator_tools/build_papers_jsonl.py

# 3) Pipeline (parse → chunk → link → embed)
.venv/bin/python parse.py
.venv/bin/python chunk.py
.venv/bin/python link.py
.venv/bin/python real_embed.py
.venv/bin/python multimodal_embed.py

# 4) Generate answer for a patient case
.venv/bin/python generate.py --patient-data-file /path/to/CASE_01.txt --vision
```

Use `fetch.py` instead of step 2 when pulling new papers from PubMed.

---

## Environment setup

On the cluster, use `scripts/install_venv.sh` to install **CPU torch first**, then `requirements.txt`, which reduces OOM kills on login nodes.

**HPC shared Python (`libpython3.10.so.1.0` error)**

`.venv/bin/python` points at the BigPurple shared Python tree. Set the library path before running:

```bash
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}
# or: module load python/gpu/3.10.6
```

### Requirements

- **Python** 3.10+
- **Packages**: see `requirements.txt` (`sentence-transformers`, `torch`, `pymupdf`, `openai`, `pillow`, etc.)
- **Email**: recommended for PubMed/Unpaywall (e.g. `you@nyu.edu`)
- **KONG_API_KEY**: required for `query_generator`, `generate`, `fetch --patient-info`

**Embed steps**: use **only this project's `.venv`**. Do not mix with other venvs (torch / typing_extensions conflicts).

```bash
.venv/bin/python real_embed.py
.venv/bin/python multimodal_embed.py
```

---

## Pipeline

| Step | Script | Description |
|------|--------|-------------|
| 1 | `fetch.py` | PubMed search → PMC OA / Unpaywall → PDF (`papers.jsonl`, `assets.jsonl`) |
| 1b | `build_papers_jsonl.py` | Rebuild `papers.jsonl` + `assets.jsonl` from `data/raw/` PDFs only |
| 2 | `parse.py` | PDF → `data/blocks.jsonl` |
| 2b | `fill_image_ocr.py` | Fill empty image OCR (**before `chunk.py`**) |
| 3 | `chunk.py` | `blocks.jsonl` → `chunks.jsonl` (full rewrite) |
| 4 | `link.py` | `(doc_id, page)` parent → `linked_chunks.jsonl` |
| 5a | `embed.py` | Hash embedding → `vectors.jsonl` (demo) |
| 5b | `real_embed.py` | BGE text only → `real_vectors.jsonl` |
| 5c | `multimodal_embed.py` | CLIP table/image → `vectors_multimodal.jsonl` |
| 6 | `retrieval.py` | Search + parent expansion (optional `--rerank`) |
| 7 | `generate.py` | Kong LLM answer → `outputs/*.md` |

### Inputs / outputs

| Script | Input | Output |
|--------|-------|--------|
| `fetch.py` | Disease name / `--patient-info` / DOI | `papers.jsonl`, `assets.jsonl`, `data/raw/{doc_id}/fulltext.pdf` |
| `build_papers_jsonl.py` | `data/raw/*.pdf`, `data/raw/{doc_id}/` | `papers.jsonl`, `assets.jsonl` |
| `parse.py` | `assets.jsonl` (or `data/assets.jsonl`) | `data/blocks.jsonl` |
| `chunk.py` | `data/blocks.jsonl` | `data/chunks.jsonl` |
| `link.py` | `data/chunks.jsonl` | `data/linked_chunks.jsonl` |
| `real_embed.py` | chunks + linked | `data/real_vectors.jsonl` |
| `multimodal_embed.py` | chunks + linked | `data/vectors_multimodal.jsonl` |
| `generate.py` | Question or `--patient-data-file`, vectors + chunks | Terminal + `outputs/{case_id}.md` |

### Incremental updates (`INCREMENTAL`)

Enabled only when `INCREMENTAL=1` / `true` / `yes`. Applies to **`fetch`**, **`real_embed`**, **`multimodal_embed`**.

- **`parse.py`**: re-parse subset with `PARSE_DOC_IDS=doc1,doc2`
- **`chunk.py` / `link.py`**: always full rebuild

---

## Multimodal embedding tips

If `multimodal_embed.py` times out on CPU:

```bash
nohup ./embed_multimodal_resume.sh 0 >> logs/_nohup_embed.out 2>&1 &
.venv/bin/python prune_multimodal_vectors.py --strip-images
nohup ./embed_multimodal_resume.sh 35 >> logs/_nohup_embed.out 2>&1 &
```

Fill image OCR only (**before `chunk.py`**):

```bash
OCR_MAX_CHARS=4000 .venv/bin/python fill_image_ocr.py pmid_23499048
```

GPU SLURM example:

```bash
srun --partition=gpu4_dev --gres=gpu:1 --cpus-per-task=4 --mem=32G --time=04:00:00 --pty bash
DEVICE=cuda BATCH_SIZE=8 INCREMENTAL=0 OCR_CLIP_FUSION_ALPHA=0.35 .venv/bin/python -u multimodal_embed.py
```

---

## Query generation (`query_generator.py`)

| Function | Purpose | Used by |
|----------|---------|---------|
| `generate_pubmed_search_queries` | Multiple short PubMed queries | `fetch.py --patient-info` |
| `generate_retrieval_query_for_treatment` | One RAG question string | `generate.py --patient-data` |

```bash
.venv/bin/python fetch.py --patient-info "65yo male, dementia, hypertension"
.venv/bin/python generate.py --patient-data "hospitalized COVID-19, renal impairment"
.venv/bin/python query_generator.py pubmed "65yo male, dementia"
.venv/bin/python query_generator.py retrieval "same patient description..."
```

---

## generate.py

Results are always saved under `outputs/` as Markdown.

- `--case-id CASE_01` → `outputs/CASE_01.md`
- `--patient-data-file CASE_01.txt` (no case-id) → `outputs/CASE_01.md`
- Question only → `outputs/result_YYYY-MM-DD_HH-MM-SS.md`

### Vision / Text-only modes

| Mode | OCR text | Image pixels | Command |
|------|:--------:|:------------:|---------|
| Vision full | ✅ | ✅ | `--vision` |
| OCR only (default) | ✅ | ❌ | (no flag) |
| Text only | ❌ | ❌ | `--text-only` |

- If both `--vision` and `--text-only` are set, text-only wins
- Saved MD includes a `Retrieval hits` table (BGE cosine or rerank score)

### Batch cases

```bash
./scripts/run_cases_vision.sh          # CASE_01 .. CASE_20
./scripts/run_cases_vision.sh 3 20     # CASE_03 .. CASE_20
```

Default case texts: `/gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts`  
Override with `export CASE_TEXT_DIR=/your/path`.

---

## Evaluation & reports

| Path | Contents |
|------|----------|
| `outputs/` | Latest generate results (`CASE_NN.md`, `CASE_NN_textOnly.md`, etc.) |
| `outputs_baseline_v1/` | Initial baseline (20 cases) |
| `reports/VISION_AB_REPORT.md` | Vision vs Text-only A/B (Korean) |
| `reports/VISION_AB_REPORT_EN.md` | Same report (English) |
| `scripts/reports/vision_two_way.py` | Recompute 2-way metrics |
| `scripts/reports/vision_three_way.py` | 3-way (vision / ocrOnly / textOnly) |

---

## Orchestrator integration

Works with the team project [`Chronic_Kidney_Disease/orchestrator`](file:///gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator/README.md): this RAG literature module + MIMIC SQL agent + patient vector DB.

| Path | Contents |
|------|----------|
| `orchestrator_runs/` | Symlink to team `orchestrator/runs/` (create locally — not in git) |
| `orchestrator_tools/run_all_8.sbatch` | SLURM batch for 8 CKD patients (`cpu_short`) |
| `orchestrator_tools/build_papers_jsonl.py` | `data/raw/` → `papers.jsonl` + `assets.jsonl` |
| `papers.jsonl` | Paper title map for orchestrator literature citations |

```bash
# Create symlink after clone (adjust path if needed)
ln -s /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator/runs orchestrator_runs

cd orchestrator_tools && sbatch run_all_8.sbatch
ls -lt ../orchestrator_runs/
```

**Warning**: do not run `python -m orchestrator.run` on the login node — use SLURM (`sbatch` / `srun`).

---

## Environment variables (summary)

| Variable | Purpose |
|----------|---------|
| `INCREMENTAL` | Incremental fetch / real_embed / multimodal_embed |
| `KONG_API_KEY`, `LLM_MODEL` | LLM (default `gpt-4o`) |
| `GENERATE_VISION`, `VISION_MAX_IMAGES`, `VISION_MAX_EDGE` | Vision in generate |
| `EMBED_MODEL`, `BATCH_SIZE`, `TEXT_WAVE_CHUNKS` | real_embed |
| `MULTIMODAL_EMBED_MODEL`, `OCR_CLIP_FUSION_ALPHA`, `MULTIMODAL_IMAGE_LIMIT` | multimodal |
| `DEVICE` | `cuda` / `cpu` / `mps` |
| `PARSE_DOC_IDS`, `OCR_BACKEND`, `OCR_ON_IMAGES`, `PARSE_NORMALIZE_JP2_IMAGES` | parse |
| `LD_LIBRARY_PATH` | BigPurple `.venv` Python |

---

## Retrieval workflow

```text
Query input
    ↓
Text DB search (real_vectors)
    ↓
[--rerank] topn → cross-encoder → topk
    ↓
Expand same-page text · table · image by parent_block_id
    ↓
Assemble context → LLM (generate)
```
