# Langone RAG + Agentic Health Framework

This repository holds the **integrated capstone codebase**. Work happens on **feature branches**; the advisor reviews and merges into **`main`**.

## Branch layout

```text
main                 ← Integration branch (advisor merges here)
├── momo             ← RAG pipeline (literature fetch, parse, embed, retrieve, generate)
└── (teammate branch) ← SQL agent + orchestration (plan-act, MIMIC, EHR)
```

| Branch | Owner | Scope |
|--------|-------|--------|
| **`main`** | Advisor / team | Stable integrated system after review |
| **`momo`** | Mo | Multimodal RAG for medical literature — see [`momo` branch README](https://github.com/MissMyPetDog/Langone-RAG-Agentic-Health-Framework/tree/momo) |
| **Teammate branch** | TBD | SQL agent, orchestrator, patient workflow |

## Workflow

1. Each member works on their own branch (`momo`, or a teammate branch such as `feature/orchestrator`).
2. Open a **Pull Request** into `main`.
3. Advisor reviews and merges when ready.
4. **`main`** becomes the single source of truth for the full agentic health framework.

## Getting started

**RAG (literature pipeline):**

```bash
git clone git@github.com:MissMyPetDog/Langone-RAG-Agentic-Health-Framework.git
cd Langone-RAG-Agentic-Health-Framework
git checkout momo
cp .env.example .env   # set KONG_API_KEY
bash scripts/install_venv.sh && source .venv/bin/activate
```

See the **`momo`** branch README for the full RAG pipeline (parse, embed, generate, BigPurple setup).

**SQL + orchestration:** clone this repo, create or checkout the orchestrator branch (name TBD by teammate), follow that branch’s README.

## Data

Large artifacts (`data/`, `outputs/`, `.venv/`) are not committed. Use shared GPFS paths or rebuild via the RAG pipeline on the `momo` branch.

## Repository

https://github.com/MissMyPetDog/Langone-RAG-Agentic-Health-Framework
