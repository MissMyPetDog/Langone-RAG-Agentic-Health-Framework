# Agentic RAG (의학 문헌)

환자·질병명 기반 PubMed·상위 저널 문헌 수집 → PDF 파싱·청킹·링킹 → 텍스트(BGE) + 멀티모달(테이블·이미지, CLIP) 벡터 DB → 검색·생성.

> English: [README_EN.md](README_EN.md)

**팀 레포**: [MissMyPetDog/Langone-RAG-Agentic-Health-Framework](https://github.com/MissMyPetDog/Langone-RAG-Agentic-Health-Framework)

```bash
git clone git@github.com:MissMyPetDog/Langone-RAG-Agentic-Health-Framework.git
cd Langone-RAG-Agentic-Health-Framework
cp .env.example .env   # KONG_API_KEY 입력
bash scripts/install_venv.sh && source .venv/bin/activate
```

`data/`는 git에 포함되지 않습니다. GPFS 공유 경로 symlink 또는 README **빠른 시작** 파이프라인으로 로컬에서 재생성하세요.

---

## 디렉터리 구조

```text
agentic_rag_kk5739/
├── fetch.py                    # PubMed 풀텍스트 수집
├── parse.py                    # PDF → blocks.jsonl
├── fill_image_ocr.py           # 이미지 OCR 보충 (chunk 전)
├── chunk.py                    # blocks → chunks
├── link.py                     # parent_block_id 부여
├── embed.py                    # hash 임베딩 (데모)
├── real_embed.py               # BGE 텍스트 임베딩
├── multimodal_embed.py         # CLIP 테이블·이미지 임베딩
├── prune_multimodal_vectors.py # 멀티모달 벡터 정리
├── embed_multimodal_resume.sh  # CPU에서 멀티모달 재개
├── retrieval.py                # 검색 + parent 확장
├── rerank.py                   # BGE + cross-encoder 2단계 (실험용)
├── generate.py                 # RAG + Kong LLM 답변 생성
├── query_generator.py          # PubMed/RAG 쿼리 LLM 생성
├── schema.py                   # JSONL TypedDict
├── vectordb.py                 # hash 벡터 데모 검색
├── requirements.txt
├── scripts/
│   ├── install_venv.sh         # venv + CPU torch 설치
│   ├── list_raw_orphans.py     # raw 폴더 vs assets.jsonl 불일치
│   ├── list_raw_orphans.sh
│   ├── run_cases_vision.sh     # CASE_01~N --vision 일괄 실행
│   └── reports/
│       ├── vision_two_way.py   # Vision vs Text-only A/B 집계
│       └── vision_three_way.py # Vision vs OCR-only vs Text-only
├── orchestrator_tools/
│   ├── build_papers_jsonl.py   # data/raw → papers.jsonl + assets.jsonl
│   └── run_all_8.sbatch        # CKD 8명 orchestrator 일괄 SLURM
├── orchestrator_runs/          # → 팀 orchestrator/runs/ symlink
├── papers.jsonl                # doc_id → title (인용·메타)
├── assets.jsonl                # doc_id → PDF 경로 (parse 입력)
├── data/
│   ├── raw/                    # 원본 PDF + 추출 figure
│   ├── blocks.jsonl            # 파싱 블록
│   ├── chunks.jsonl            # 청크
│   ├── linked_chunks.jsonl     # parent 링크
│   ├── real_vectors.jsonl      # BGE 텍스트 벡터
│   └── vectors_multimodal.jsonl
├── outputs/                    # generate.py 최신 결과 (CASE_01~20 등)
├── outputs_baseline_v1/        # 초기 baseline CASE_01~20
├── reports/                    # Vision A/B 분석 리포트 (MD)
└── logs/                       # 실행 로그 (_mm_regen, ocronly_batch 등)
```

---

## 현재 코퍼스 (2026-05)

| doc_id | 제목 (요약) | source |
|--------|-------------|--------|
| `gilbert_acc_weight_2025` | ACC 2025 Medical Weight Management | manual |
| `ndumele_aha_ckm_2023` | AHA CKM Presidential Advisory | manual |
| `ndumele_ckm_synopsis_2023` | AHA CKM Synopsis | manual |
| `nihms_1913084` | Life's Essential 8 (AHA) | pubmed_central |
| `pmid_23499048` | KDIGO 2012 AKI Guideline | pubmed |

**데이터 규모 (최근 빌드 기준)**

| 파일 | 행 수 |
|------|------:|
| `blocks.jsonl` | 1,221 |
| `chunks.jsonl` / `linked_chunks.jsonl` | 2,386 |
| `real_vectors.jsonl` | 2,345 (text만) |
| `vectors_multimodal.jsonl` | 41 (table+image) |

PDF를 `data/raw/`에 넣거나 `fetch.py`로 받은 뒤, 메타는 `orchestrator_tools/build_papers_jsonl.py`로 `papers.jsonl` + `assets.jsonl`을 함께 갱신합니다.

---

## 빠른 시작

```bash
# 1) 환경
bash scripts/install_venv.sh
source .venv/bin/activate
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}
export KONG_API_KEY=...

# 2) 수동 PDF 코퍼스 (이미 data/raw/에 PDF가 있을 때)
.venv/bin/python orchestrator_tools/build_papers_jsonl.py

# 3) 파이프라인 (parse → chunk → link → embed)
.venv/bin/python parse.py
.venv/bin/python chunk.py
.venv/bin/python link.py
.venv/bin/python real_embed.py
.venv/bin/python multimodal_embed.py

# 4) 환자 케이스 답변 생성
.venv/bin/python generate.py --patient-data-file /path/to/CASE_01.txt --vision
```

PubMed에서 새 논문을 가져올 때는 2) 대신 `fetch.py`를 사용합니다.

---

## 환경 준비

클러스터에서 venv를 새로 만들 때는 `scripts/install_venv.sh`를 쓰면 로그인 노드 OOM을 줄이기 위해 **CPU용 torch를 먼저** 깐 뒤 `requirements.txt`를 설치합니다.

**HPC 공유 Python (`libpython3.10.so.1.0` 오류)**

`.venv/bin/python`은 bigpurple 공유 Python을 참조합니다. 실행 전에 라이브러리 경로를 잡아주세요.

```bash
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}
# 또는: module load python/gpu/3.10.6
```

### 요구 사항

- **Python** 3.10+
- **패키지**: `requirements.txt` (`sentence-transformers`, `torch`, `pymupdf`, `openai`, `pillow` 등)
- **이메일**: PubMed/Unpaywall (`kk5739@nyu.edu` 등)
- **KONG_API_KEY**: `query_generator`, `generate`, `fetch --patient-info`

**Embed 단계**: 다른 venv와 섞지 말고 **프로젝트 `.venv`만** 사용하세요.

```bash
.venv/bin/python real_embed.py
.venv/bin/python multimodal_embed.py
```

---

## 파이프라인

| 단계 | 스크립트 | 설명 |
|------|----------|------|
| 1 | `fetch.py` | PubMed 검색 → PMC OA / Unpaywall → PDF (`papers.jsonl`, `assets.jsonl`) |
| 1b | `build_papers_jsonl.py` | `data/raw/` PDF만으로 `papers.jsonl` + `assets.jsonl` 재생성 |
| 2 | `parse.py` | PDF → `data/blocks.jsonl` |
| 2b | `fill_image_ocr.py` | 빈 이미지 OCR 보충 (**`chunk.py` 전**) |
| 3 | `chunk.py` | `blocks.jsonl` → `chunks.jsonl` (전체 덮어쓰기) |
| 4 | `link.py` | `(doc_id, page)` parent → `linked_chunks.jsonl` |
| 5a | `embed.py` | hash 임베딩 → `vectors.jsonl` (데모) |
| 5b | `real_embed.py` | BGE 텍스트만 → `real_vectors.jsonl` |
| 5c | `multimodal_embed.py` | CLIP table/image → `vectors_multimodal.jsonl` |
| 6 | `retrieval.py` | 검색 + parent 확장 (`--rerank` 선택) |
| 7 | `generate.py` | Kong LLM 답변 + `outputs/*.md` 저장 |

### 입·출력

| 스크립트 | 입력 | 출력 |
|----------|------|------|
| `fetch.py` | 질병명 / `--patient-info` / DOI | `papers.jsonl`, `assets.jsonl`, `data/raw/{doc_id}/fulltext.pdf` |
| `build_papers_jsonl.py` | `data/raw/*.pdf`, `data/raw/{doc_id}/` | `papers.jsonl`, `assets.jsonl` |
| `parse.py` | `assets.jsonl` (또는 `data/assets.jsonl`) | `data/blocks.jsonl` |
| `chunk.py` | `data/blocks.jsonl` | `data/chunks.jsonl` |
| `link.py` | `data/chunks.jsonl` | `data/linked_chunks.jsonl` |
| `real_embed.py` | chunks + linked | `data/real_vectors.jsonl` |
| `multimodal_embed.py` | chunks + linked | `data/vectors_multimodal.jsonl` |
| `generate.py` | 질문 또는 `--patient-data-file`, 벡터·청크 | 터미널 + `outputs/{case_id}.md` |

### 증분 업데이트 (`INCREMENTAL`)

`INCREMENTAL=1` / `true` / `yes`일 때만 켜짐. 적용: **`fetch`**, **`real_embed`**, **`multimodal_embed`**.

- **`parse.py`**: `PARSE_DOC_IDS=doc1,doc2`로 일부 doc만 재파싱 가능
- **`chunk.py` / `link.py`**: 항상 전체 재생성

---

## 멀티모달 임베딩 팁

CPU에서 `multimodal_embed.py`가 끊기면:

```bash
nohup ./embed_multimodal_resume.sh 0 >> logs/_nohup_embed.out 2>&1 &
.venv/bin/python prune_multimodal_vectors.py --strip-images
nohup ./embed_multimodal_resume.sh 35 >> logs/_nohup_embed.out 2>&1 &
```

이미지 OCR만 먼저 채울 때 (`chunk.py` **이전**):

```bash
OCR_MAX_CHARS=4000 .venv/bin/python fill_image_ocr.py pmid_23499048
```

GPU SLURM 예시:

```bash
srun --partition=gpu4_dev --gres=gpu:1 --cpus-per-task=4 --mem=32G --time=04:00:00 --pty bash
DEVICE=cuda BATCH_SIZE=8 INCREMENTAL=0 OCR_CLIP_FUSION_ALPHA=0.35 .venv/bin/python -u multimodal_embed.py
```

---

## Query Generation (`query_generator.py`)

| 함수 | 용도 | 연결 |
|------|------|------|
| `generate_pubmed_search_queries` | PubMed 검색어 여러 개 | `fetch.py --patient-info` |
| `generate_retrieval_query_for_treatment` | RAG 질문 한 줄 | `generate.py --patient-data` |

```bash
.venv/bin/python fetch.py --patient-info "65yo male, dementia, hypertension"
.venv/bin/python generate.py --patient-data "hospitalized COVID-19, renal impairment"
.venv/bin/python query_generator.py pubmed "65yo male, dementia"
.venv/bin/python query_generator.py retrieval "동일한 환자 서술..."
```

---

## generate.py

결과는 항상 `outputs/`에 MD로 저장됩니다.

- `--case-id CASE_01` → `outputs/CASE_01.md`
- `--patient-data-file CASE_01.txt` (case-id 생략) → `outputs/CASE_01.md`
- 질문만 → `outputs/result_YYYY-MM-DD_HH-MM-SS.md`

### Vision / Text-only 모드

| 모드 | OCR 텍스트 | 이미지 픽셀 | 명령 |
|------|:---:|:---:|------|
| Vision full | ✅ | ✅ | `--vision` |
| OCR only (default) | ✅ | ❌ | (플래그 없음) |
| Text only | ❌ | ❌ | `--text-only` |

- `--vision` + `--text-only` 동시 지정 시 text-only 우선
- MD 상단에 `Retrieval hits` 표(BGE cosine 또는 rerank score) 포함

### 케이스 배치

```bash
./scripts/run_cases_vision.sh          # CASE_01 .. CASE_20
./scripts/run_cases_vision.sh 3 20     # CASE_03 .. CASE_20
```

기본 케이스 텍스트: `/gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts`

---

## 평가·리포트

| 경로 | 내용 |
|------|------|
| `outputs/` | 최신 generate 결과 (`CASE_NN.md`, `CASE_NN_textOnly.md` 등) |
| `outputs_baseline_v1/` | 초기 baseline 20케이스 |
| `reports/VISION_AB_REPORT.md` | Vision vs Text-only A/B (한국어) |
| `reports/VISION_AB_REPORT_EN.md` | 동일 리포트 (영어) |
| `scripts/reports/vision_two_way.py` | 2-way 메트릭 재집계 |
| `scripts/reports/vision_three_way.py` | 3-way (vision / ocrOnly / textOnly) |

---

## Orchestrator 통합

팀 프로젝트 [`Chronic_Kidney_Disease/orchestrator`](file:///gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator/README.md)와 연동합니다. 본 RAG literature + MIMIC SQL agent + 환자 vector DB를 함께 호출합니다.

| 경로 | 내용 |
|------|------|
| `orchestrator_runs/` | 팀 `orchestrator/runs/` symlink |
| `orchestrator_tools/run_all_8.sbatch` | CKD 8명 일괄 SLURM (`cpu_short`) |
| `orchestrator_tools/build_papers_jsonl.py` | `data/raw/` → `papers.jsonl` + `assets.jsonl` |
| `papers.jsonl` | orchestrator literature 인용 제목 매핑 |

```bash
cd orchestrator_tools && sbatch run_all_8.sbatch
ls -lt ../orchestrator_runs/
```

**주의**: login node에서 `python -m orchestrator.run` 직접 실행 금지 → SLURM(`sbatch` / `srun`) 사용.

---

## 환경 변수 (요약)

| 변수 | 용도 |
|------|------|
| `INCREMENTAL` | fetch / real_embed / multimodal_embed 증분 |
| `KONG_API_KEY`, `LLM_MODEL` | LLM (`gpt-4o` 기본) |
| `GENERATE_VISION`, `VISION_MAX_IMAGES`, `VISION_MAX_EDGE` | generate 비전 |
| `EMBED_MODEL`, `BATCH_SIZE`, `TEXT_WAVE_CHUNKS` | real_embed |
| `MULTIMODAL_EMBED_MODEL`, `OCR_CLIP_FUSION_ALPHA`, `MULTIMODAL_IMAGE_LIMIT` | multimodal |
| `DEVICE` | `cuda` / `cpu` / `mps` |
| `PARSE_DOC_IDS`, `OCR_BACKEND`, `OCR_ON_IMAGES`, `PARSE_NORMALIZE_JP2_IMAGES` | parse |
| `LD_LIBRARY_PATH` | bigpurple `.venv` Python |

---

## 검색 워크플로우

```text
쿼리 입력
    ↓
텍스트 DB 검색 (real_vectors)
    ↓
[--rerank] topn → cross-encoder → topk
    ↓
parent_block_id 기준 같은 페이지 text·table·image 확장
    ↓
컨텍스트 조립 → LLM (generate)
```
