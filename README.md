source .venv/bin/activate 

## Agentic RAG (의학 문헌)

환자 질병명 기반 PubMed·상위 저널(Nature, Lancet, JAMA, BMJ, NEJM) 문헌 수집 → 파싱·청킹·링킹 → 텍스트(BGE) + 멀티모달(테이블·이미지, CLIP) 벡터 DB 구축 → 검색/생성.

### 요구 사항

- **Python**: 3.10+
- **패키지**: `typing_extensions`, `sentence-transformers`, `torch`, `python-dotenv`, `pymupdf`, `pillow` 등
- **이메일**: PubMed/Unpaywall 사용 시 이메일 설정 권장 (예: `kk5739@nyu.edu`)
- **Kong API 키**: `KONG_API_KEY` (generate 단계)

**Embed 단계(5–6)**: 클러스터에서 다른 venv(예: `rag_venv`)와 섞이면 torch/typing_extensions 충돌이 납니다.  
→ 반드시 **프로젝트 `.venv`만 사용**하세요.  
→ `real_embed.py`, `multimodal_embed.py` 실행 시:

```bash
.venv/bin/python real_embed.py
.venv/bin/python multimodal_embed.py
```

### 파이프라인 순서

| 단계 | 스크립트 | 설명 |
|------|----------|------|
| 1 | `fetch.py` | 질병명으로 PubMed 검색, PMC OA → Unpaywall → 풀텍스트 수집 (`papers.jsonl`, `assets.jsonl`) |
| 2 | `parse.py` | PDF/TXT에서 텍스트·테이블·이미지 블록 추출 → `data/blocks.jsonl` |
| 3 | `chunk.py` | 텍스트 슬라이딩 윈도우, 테이블/이미지 1블록=1청크 → `data/chunks.jsonl` |
| 4 | `link.py` | (doc_id, page)로 `parent_block_id` 부여 → `data/linked_chunks.jsonl` |
| 5a | `embed.py` | hash 기반 임베딩 → `data/vectors.jsonl` |
| 5b | `real_embed.py` | BGE 텍스트 임베딩 → `data/real_vectors.jsonl` |
| 5c | `multimodal_embed.py` | CLIP 테이블·이미지 임베딩 → `data/vectors_multimodal.jsonl` |
| 6 | `retrieval.py` | 쿼리 → 텍스트 검색 + parent 확장. `--rerank` 시 cross-encoder 재순위 |
| 7 | `generate.py` | Kong API로 답변 생성. `--rerank` 옵션 지원 |

### 스크립트별 입·출력

| 스크립트 | 입력 | 출력 |
|----------|------|------|
| `fetch.py` | 질병명 인자, (선택) 기존 `papers.jsonl`·`assets.jsonl` | `papers.jsonl`, `assets.jsonl`, `data/raw/{doc_id}/fulltext.pdf` |
| `parse.py` | `data/assets.jsonl` 또는 `assets.jsonl` | `data/blocks.jsonl` |
| `chunk.py` | `data/blocks.jsonl` | `data/chunks.jsonl` |
| `link.py` | `data/chunks.jsonl` | `data/linked_chunks.jsonl` |
| `embed.py` | `data/chunks.jsonl`, `data/linked_chunks.jsonl` | `data/vectors.jsonl` |
| `real_embed.py` | `data/chunks.jsonl`, `data/linked_chunks.jsonl` | `data/real_vectors.jsonl` |
| `multimodal_embed.py` | `data/chunks.jsonl`, `data/linked_chunks.jsonl` | `data/vectors_multimodal.jsonl` |
| `retrieval.py` | 쿼리 인자, `data/real_vectors.jsonl`(또는 `vectors.jsonl`), `data/linked_chunks.jsonl`, `data/chunks.jsonl` | 터미널 출력 (검색 결과·확장 청크) |
| `generate.py` | 질문 인자, 위 벡터·청크·linked_chunks, `papers.jsonl` | 터미널 출력 (답변·인용·사용 소스) |

### 증분 업데이트 (INCREMENTAL=1)

이미 한 번 파이프라인을 돌린 뒤, **새 논문만 추가**하고 싶을 때 사용. 기존 데이터는 유지하고 신규만 처리해 시간·비용을 줄임.

| 단계 | INCREMENTAL=1 동작 |
|------|---------------------|
| **fetch** | 기존 `papers.jsonl`/`assets.jsonl`의 doc_id 확인 → PubMed에서 **새 논문만** 가져와 뒤에 append |
| **parse** | 기존 `blocks.jsonl`의 doc_id 확인 → **새 doc만** 파싱해 기존 blocks 뒤에 append |
| **chunk** | 기존 `chunks.jsonl`의 doc_id 확인 → **새 doc 블록만** 청킹해 기존 chunks 뒤에 append |
| **link** | 항상 **전체** `chunks.jsonl` 기준으로 `linked_chunks.jsonl` **전체 재생성** (기존+신규 모두 반영) |
| **real_embed** | 기존 `real_vectors.jsonl`의 chunk_id 확인 → **새 텍스트 청크만** 임베딩해 기존 벡터 뒤에 append |
| **multimodal_embed** | 기존 `vectors_multimodal.jsonl`의 chunk_id 확인 → **새 table/image 청크만** 임베딩해 append |

**link만** 증분 없이 전체 재생성. 나머지는 기존 결과를 유지한 채 새 것만 추가.

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

### 환경 변수

- `INCREMENTAL=1`: 증분 업데이트 (기존 유지 + 새 것만 추가)
- `KONG_API_KEY`: generate용 API 키
- `EMBED_MODEL`, `BATCH_SIZE`: real_embed (기본 BGE)
- `MULTIMODAL_EMBED_MODEL`: multimodal_embed (기본 clip-ViT-B-32)

#### Embed 속도 올리기

- **GPU 사용**: `DEVICE`를 지정하지 않으면 자동으로 CUDA 사용. CPU만 쓰려면 `DEVICE=cpu`.
- **real_embed**: 기본 `BATCH_SIZE=1`(OOM 방지). **GPU 있을 때** `BATCH_SIZE=32` 또는 `64`로 올리면 체감 속도 크게 향상.  
  예: `BATCH_SIZE=32 .venv/bin/python real_embed.py`
- **multimodal_embed**: 테이블/이미지를 배치로 인코딩. 기본 배치 16. 메모리 부족하면 `BATCH_SIZE=8`로 낮추기.

