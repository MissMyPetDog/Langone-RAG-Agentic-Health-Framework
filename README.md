# Agentic RAG (의학 문헌)

환자 질병명 기반 PubMed·상위 저널(Nature, Lancet, JAMA, BMJ, NEJM) 문헌 수집 → 파싱·청킹·링킹 → 텍스트(BGE) + 멀티모달(테이블·이미지, CLIP) 벡터 DB 구축 → 검색/생성.

### 환경 준비

클러스터 등에서 venv를 새로 만들 때는 `scripts/install_venv.sh`를 쓰면 로그인 노드 OOM을 줄이기 위해 **CPU용 torch를 먼저** 깐 뒤 `requirements.txt`를 설치합니다.

```bash
bash scripts/install_venv.sh
source .venv/bin/activate
```

### 요구 사항

- **Python**: 3.10+
- **패키지**: `typing_extensions`, `sentence-transformers`, `torch`, `python-dotenv`, `openai`, `pymupdf`, `pillow` 등 (`requirements.txt`)
- **이메일**: PubMed/Unpaywall 사용 시 이메일 설정 권장 (예: `kk5739@nyu.edu`)
- **Kong API 키**: `KONG_API_KEY` (`query_generator`·`generate`·`fetch --patient-info` 등 LLM 호출 시)

**Embed 단계(5–6)**: 클러스터에서 다른 venv(예: `rag_venv`)와 섞이면 torch/typing_extensions 충돌이 납니다.  
→ 반드시 **프로젝트 `.venv`만 사용**하세요.  
→ `real_embed.py`, `multimodal_embed.py` 실행 시:

```bash
.venv/bin/python real_embed.py
.venv/bin/python multimodal_embed.py
```

**CPU에서 `multimodal_embed.py`가 세션 시간 안에 끝나지 않을 때**: 환경 변수 `MULTIMODAL_IMAGE_LIMIT=1`과 `INCREMENTAL=1`로 한 장씩 저장하며 재실행할 수 있습니다. 편의용 스크립트 `embed_multimodal_resume.sh`는 루프 안에서 **`BATCH_SIZE=1`**, **`MULTIMODAL_IMAGE_LIMIT=1`** 로 고정해 로그인 노드에서도 끊기지 않게 합니다(직접 `multimodal_embed.py`를 호출할 때는 기본 배치 16 등이 적용됨).

```bash
# 목표 행 수(embed_multimodal_resume.sh 내부 Python과 동일: linked_chunks+chunks 기준 유효 table+image 청크 수)까지 α=0으로 채움
nohup ./embed_multimodal_resume.sh 0 >> _nohup_embed.out 2>&1 &

# 위가 끝난 뒤, 이미지 modality 행만 제거한 뒤 OCR+CLIP 융합(α=0.35)으로 이미지 재임베딩
.venv/bin/python prune_multimodal_vectors.py --strip-images
nohup ./embed_multimodal_resume.sh 35 >> _nohup_embed.out 2>&1 &
```

**`--strip-images` 주의**: 테이블 멀티모달 대상이 없고 **이미지 청크만** 있으면, 이미지 행을 모두 지우므로 `vectors_multimodal.jsonl`이 비게 됩니다. 이 경우 `embed_multimodal_resume.sh 35`가 TARGET까지 **전부 α=0.35로 다시 채우는** 흐름이 됩니다(테이블 벡터를 남겨 두려는 시나리오와 다름).

`parse.py`와 분리해 `blocks.jsonl`의 빈 이미지 OCR만 채울 때는 `fill_image_ocr.py`(doc_id 인자 1개). **`chunk.py`보다 먼저** 돌려야 청크의 `text`에 OCR이 들어갑니다.

```bash
OCR_MAX_CHARS=4000 .venv/bin/python fill_image_ocr.py pmid_23499048
```

오래된 `vectors_multimodal.jsonl` 행을 현재 청크 집합에 맞출 때는 인자 없이 `prune_multimodal_vectors.py`, 이미지 행만 지울 때는 `--strip-images`.

**코퍼스·청크를 갈아엎은 뒤** `vectors_multimodal.jsonl`에 예전 `doc_id`가 남아 있으면 파일을 지우거나 비운 다음 `INCREMENTAL=0`으로 `multimodal_embed.py`를 다시 실행하는 편이 안전합니다. 같은 출력 파일을 두고 **`multimodal_embed.py`를 동시에 여러 번** 돌리지 마세요.

### 파이프라인 순서

| 단계 | 스크립트 | 설명 |
|------|----------|------|
| 1 | `fetch.py` | 질병명으로 PubMed 검색, PMC OA → Unpaywall → 풀텍스트 수집 (`papers.jsonl`, `assets.jsonl`) |
| 2 | `parse.py` | PDF/TXT에서 텍스트·테이블·이미지 블록 추출 → `data/blocks.jsonl` (선택: `PARSE_DOC_IDS`, `OCR_BACKEND`, `OCR_ON_IMAGES`, `PARSE_NORMALIZE_JP2_IMAGES` 기본 1=`.jpx`/`.jp2`/`.j2k`→PNG) |
| 2b (선택) | `fill_image_ocr.py` | 이미지 블록 빈 `text`만 RapidOCR로 채움. **반드시 `chunk.py` 전** |
| 3 | `chunk.py` | `blocks.jsonl` 전체를 읽어 **`chunks.jsonl`을 매번 통째로 다시 씀** (증분 없음) |
| 4 | `link.py` | (doc_id, page)로 `parent_block_id` 부여 → `linked_chunks.jsonl` **전체 재생성** |
| 5a | `embed.py` | hash 기반 임베딩 → `data/vectors.jsonl` |
| 5b | `real_embed.py` | **`modality == text` 청크만** BGE 임베딩 → `data/real_vectors.jsonl` (이미지/테이블 행 수만큼 줄 수가 `chunks.jsonl`보다 적을 수 있음) |
| 5c | `multimodal_embed.py` | CLIP 테이블·이미지 임베딩 → `data/vectors_multimodal.jsonl` (`MULTIMODAL_IMAGE_LIMIT`, `OCR_CLIP_FUSION_ALPHA`, `DEVICE`) |
| 보조 | `prune_multimodal_vectors.py` | `vectors_multimodal.jsonl`에서 무효 chunk 제거 또는 `--strip-images` |
| 보조 | `embed_multimodal_resume.sh` | CPU에서 멀티모달 임베딩을 끊어서 재개 (`0` 또는 `35`) |
| 6 | `retrieval.py` | 쿼리 → 텍스트 검색 + parent 확장. `--rerank` 시 cross-encoder 재순위 |
| 7 | `generate.py` | Kong API로 답변 생성. `--rerank`, `--dry-run`, `--patient-data` / `--patient-data-file`, **`--vision`**(figure를 `image_url`로 전달). 결과 자동 MD 저장 |
| (단독) | `rerank.py` | BGE 검색 + cross-encoder 재순위 2단계(실험·디버그용 CLI) |
| (참고) | `schema.py` | JSONL 레코드 TypedDict 정의 |
| (참고) | `vectordb.py` | hash 임베딩(`embed.py`와 동일 계열) 데모 검색 |
| (유틸) | `scripts/list_raw_orphans.py` | `data/raw`에만 있고 `assets.jsonl`에 없는 doc_id 나열 |
| (유틸) | `scripts/run_cases_vision.sh` | `CASE_01`~`CASE_N`에 대해 `generate.py --vision` 일괄 실행 (인자: 시작·끝 번호, 선택 `CASE_TEXT_DIR`) |

### 스크립트별 입·출력

| 스크립트 | 입력 | 출력 |
|----------|------|------|
| `fetch.py` | 질병명 인자 또는 `--patient-info`, (선택) 기존 `papers.jsonl`·`assets.jsonl` | `papers.jsonl`, `assets.jsonl`, `data/raw/{doc_id}/fulltext.pdf` |
| `parse.py` | `data/assets.jsonl` 또는 `assets.jsonl` | `data/blocks.jsonl` |
| `chunk.py` | `data/blocks.jsonl` | `data/chunks.jsonl` |
| `link.py` | `data/chunks.jsonl` | `data/linked_chunks.jsonl` |
| `embed.py` | `data/chunks.jsonl`, `data/linked_chunks.jsonl` | `data/vectors.jsonl` |
| `real_embed.py` | `data/chunks.jsonl`, `data/linked_chunks.jsonl` | `data/real_vectors.jsonl` |
| `multimodal_embed.py` | `data/chunks.jsonl`, `data/linked_chunks.jsonl` | `data/vectors_multimodal.jsonl` |
| `retrieval.py` | 쿼리 인자, `data/real_vectors.jsonl`(또는 `vectors.jsonl`), `data/linked_chunks.jsonl`, `data/chunks.jsonl` | 터미널 출력 (검색 결과·확장 청크) |
| `generate.py` | 질문 인자 또는 `--patient-data` / `--patient-data-file`, 위 벡터·청크·linked_chunks, `papers.jsonl` | 터미널 출력 + `outputs/{case_id}.md` 또는 `outputs/result_*.md` 자동 저장 (`--case-id` 생략 시 patient 파일 basename 사용) |
| `query_generator.py` | 환자/케이스 서술 문자열, `KONG_API_KEY` | 표준출력에 PubMed용 검색어(여러 개) 또는 RAG용 질문(한 줄) |
| `fill_image_ocr.py` | `data/blocks.jsonl`, doc_id 인자 | 같은 파일 갱신(해당 doc의 빈 이미지 OCR만). **`chunk.py` 이전**에 실행 |
| `prune_multimodal_vectors.py` | `vectors_multimodal.jsonl`, `chunks`/`linked_chunks` | 정리된 `vectors_multimodal.jsonl` |

### 증분 업데이트 (`INCREMENTAL`)

환경 변수 **`INCREMENTAL`은 숫자 단계가 아니라 스위치**입니다. 값이 `1` / `true` / `yes`(소문자)일 때만 켜지고, **`0`·미설정·그 외 문자열은 모두 꺼짐**으로 처리됩니다.

**`INCREMENTAL=1`이 실제로 적용되는 단계** (`fetch`, `real_embed`, `multimodal_embed`):

| 단계 | `INCREMENTAL=1`일 때 |
|------|---------------------|
| **fetch** | 기존 `papers.jsonl`/`assets.jsonl`의 doc_id를 보고 PubMed에서 **새 논문만** 가져와 뒤에 append |
| **real_embed** | 기존 `real_vectors.jsonl`의 `chunk_id`는 건너뛰고 **새 텍스트 청크만** append |
| **multimodal_embed** | 기존 `vectors_multimodal.jsonl`의 `chunk_id`는 건너뛰고 **새 table/image만** append. 켜져 있을 때는 배치마다 파일에 flush. `MULTIMODAL_IMAGE_LIMIT`로 이미지 N장만 처리 후 종료 가능 |

**`parse.py`**: `INCREMENTAL`을 읽지 않습니다. `assets.jsonl`에 있는 문서를 전부 다시 파싱해 `blocks.jsonl`을 갱신합니다. **일부 doc만 다시 파싱**할 때는 `PARSE_DOC_IDS=doc1,doc2` — 이때만 기존 `blocks.jsonl`에서 해당 doc 행을 빼고 나머지 doc 블록과 합칩니다.

**`chunk.py`**: `INCREMENTAL` 없음. **`blocks.jsonl` 전체 → `chunks.jsonl` 전체 덮어쓰기**이므로, 블록을 바꾼 뒤에는 항상 `chunk` → `link`를 다시 돌립니다.

**`link.py`**: 항상 `chunks.jsonl` 전체를 읽어 `linked_chunks.jsonl`을 **통째로 다시 씀**.

### 검색 워크플로우

```text
쿼리 입력
    ↓
텍스트 DB 검색 (real_vectors 또는 vectors)
    ↓
[--rerank 시] topn 후보 → cross-encoder rerank → topk
    ↓
매칭된 parent_block_id에 대해 같은 페이지의 텍스트·테이블·이미지 확장
    ↓
컨텍스트 조립 → LLM (generate 시)
```

### Optimized Query Generation (`query_generator.py`)

환자·케이스 서술을 넣으면 Kong(LLM)으로 **두 종류**의 문구를 만들 수 있습니다. 둘 다 `KONG_API_KEY`(및 선택 `LLM_MODEL`, 기본 `gpt-4o`)가 필요합니다. 키가 없으면 API를 부르지 않고 입력 문자열을 그대로 씁니다.

| 구분 | 모듈 함수 | 용도 | 파이프라인에서의 연결 |
|------|-----------|------|------------------------|
| **1-1** | `generate_pubmed_search_queries` | PubMed에 넣기 좋은 **짧은 검색어 여러 개** (상위 1개가 `fetch` 검색어로 사용) | `fetch.py --patient-info "..."` 가 내부에서 호출 |
| **1-2** | `generate_retrieval_query_for_treatment` | 시맨틱 검색·근거 조회용 **질문 한 덩어리** (치료/진단 맥락 반영) | `generate.py --patient-data "..."` 가 내부에서 호출 |

**통합 실행 (권장)**

```bash
export KONG_API_KEY=...

# 1-1 → 생성된 쿼리로 PubMed fetch까지 이어짐
.venv/bin/python fetch.py --patient-info "65yo male, dementia, hypertension, on ACE inhibitor"

# 1-2 → 생성된 질문으로 retrieval 후 Kong으로 답변 생성
.venv/bin/python generate.py --patient-data "hospitalized COVID-19, diabetes, renal impairment, dexamethasone consideration"
```

**`query_generator.py`만 단독 실행** (쿼리만 보고 싶을 때)

```bash
export KONG_API_KEY=...

# PubMed용 검색어 여러 줄 출력
.venv/bin/python query_generator.py pubmed "65yo male, dementia, hypertension"
# 선택: -n 5 로 최대 개수 조정

# RAG retrieval / generate에 넣을 질문 한 줄 출력
.venv/bin/python query_generator.py retrieval "동일한 환자 서술..."
```

`retrieval.py`는 질문 문자열만 인자로 받으므로, `query_generator.py retrieval ...` 출력을 복사해 `.venv/bin/python retrieval.py "복사한 질문"` 에 넣어도 됩니다.

### generate.py 결과 자동 저장·비전·케이스 배치

`generate.py` 실행 후 결과가 **항상** `outputs/` 폴더에 MD 파일로 저장됩니다.

- `--case-id` 지정 시: `outputs/{case_id}.md`
- `--patient-data-file`만 쓰고 `--case-id` 생략 시: 파일 basename(예: `CASE_01.txt` → `outputs/CASE_01.md`)
- 위 둘 다 없고 질문만 있을 때: `outputs/result_YYYY-MM-DD_HH-MM-SS.md`

**`--vision`**: 검색에 걸린 figure를 디스크에서 읽어 API에 `image_url`(base64 data URL)로 붙입니다. RAG용 CLIP 벡터와는 별개이며, **비전 가능 모델**(기본 `gpt-4o`)이어야 합니다. 환경 변수 `GENERATE_VISION=1`로 플래그와 동일하게 켤 수 있음. `VISION_MAX_IMAGES`(기본 6), `VISION_MAX_EDGE`(기본 1536, 긴 변 기준 리사이즈 후 JPEG).

**Used Sources / 답변 텍스트**: 디스크에 `stem.png`가 있으면 chunk의 `asset_path`가 `.jpx` 등이어도 **미리보기·컨텍스트에는 PNG 경로를 우선**합니다. LLM 본문에 잘못된 `.jpx` 경로가 나오면 저장 전에 figure 경로만 `.png`로 치환하는 후처리가 들어갑니다.

**케이스 여러 개 (`CASE_01`~`CASE_20` 등)**:

```bash
cd /gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739
export LD_LIBRARY_PATH="/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}"
D=/gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts
for n in $(seq 1 20); do

  i=$(printf 'CASE_%02d' "$n")
  ./.venv/bin/python generate.py --patient-data-file "$D/${i}.txt" --vision
done
```

또는 `./scripts/run_cases_vision.sh 3 20` (기본 `CASE_TEXT_DIR`는 위와 동일 경로).

### 환경 변수

- `INCREMENTAL`: `1` / `true` / `yes`만 증분 ON (`fetch`, `real_embed`, `multimodal_embed`). `0`이나 비우면 OFF(전체 재임베딩 시 기존 벡터 파일을 덮어쓰거나, multimodal은 끝에 한 번 flush)
- `KONG_API_KEY`: Kong LLM (`generate`, `query_generator`, `fetch --patient-info` 등)
- `LLM_MODEL`: `query_generator`·`generate` 등에서 사용할 모델명 (미설정 시 `gpt-4o`)
- **`generate` + 비전**: `GENERATE_VISION=1`(또는 CLI `--vision`), `VISION_MAX_IMAGES`, `VISION_MAX_EDGE`
- `EMBED_MODEL`, `BATCH_SIZE`: real_embed (기본 BGE)
- `TEXT_WAVE_CHUNKS`: real_embed에서 본문을 몇 개 청크씩만 RAM에 올릴지 (기본 512; OOM 시 256 등). `0`이면 전부 한 번에 로드.
- `MULTIMODAL_EMBED_MODEL`: multimodal_embed (기본 clip-ViT-B-32)
- `OCR_CLIP_FUSION_ALPHA`: 이미지 임베딩 시 CLIP vs OCR 텍스트 벡터 가중 (0=이미지만, 1=텍스트만; 기본 0.35)
- `MULTIMODAL_IMAGE_LIMIT`: 양의 정수면 이미지를 그 개수만 인코딩하고 종료(재실행으로 이어서 처리)
- `DEVICE`: `cuda` \| `cpu` \| `mps`. 미설정 시 CUDA 가능하면 `cuda`, 아니면 `cpu`
- **parse**: `PARSE_DOC_IDS`, `OCR_BACKEND`, `OCR_ON_IMAGES`, `OCR_MAX_CHARS`, `EASYOCR_LANGS`, `PARSE_NORMALIZE_JP2_IMAGES`(기본 1: JPEG2000 figure를 PNG로 저장; 미리보기·호환용, `0`이면 PDF 내장 바이트 그대로)
- **fill_image_ocr**: `OCR_MAX_CHARS` 등
- 클러스터에서 `.venv/bin/python`이 `libpython3.10.so`를 못 찾으면(예):  
  `export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH}`

#### SLURM GPU 대화형 세션 (예시)

로그인 노드에서 GPU가 필요한 작업(`real_embed`, `multimodal_embed`, `generate.py --rerank` 등)은 **GPU 파티션에서 대화형 셸**을 연 뒤 실행하는 것을 권장합니다.

```bash
srun --partition=gpu4_dev --gres=gpu:1 --cpus-per-task=4 --mem=32G --time=04:00:00 --pty bash
```

할당 후 `nvidia-smi`로 GPU가 보이는지 확인하세요.

#### Embed 속도 올리기

- **GPU 사용**: `DEVICE`를 비우면 CUDA가 있으면 `cuda`, 없으면 `cpu`. CPU만 강제하려면 `DEVICE=cpu`.
- **real_embed**: 기본 `BATCH_SIZE=1`(OOM 방지). **GPU 있을 때** `BATCH_SIZE=32` 또는 `64`로 올리면 체감 속도 크게 향상.  
  예: `BATCH_SIZE=32 .venv/bin/python real_embed.py`
- **multimodal_embed**: 테이블/이미지를 배치로 인코딩. 기본 `BATCH_SIZE=16`. GPU 메모리가 부족하면 `8` 등으로 낮추기. 로그인 노드(CPU)에서는 한 번에 끝까지 쓰려면 `INCREMENTAL=0`이어도 되지만 시간이 오래 걸릴 수 있음.  
  SLURM GPU 노드에서 처음부터 다시 채우기 예:  
  `export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH}`  
  `DEVICE=cuda BATCH_SIZE=8 INCREMENTAL=0 OCR_CLIP_FUSION_ALPHA=0.35 .venv/bin/python -u multimodal_embed.py`
- **`embed_multimodal_resume.sh`**: 내부적으로 배치 1·이미지 1장 단위로만 돌리므로, 대량 작업은 GPU에서 위처럼 직접 호출하는 편이 빠를 수 있음.

