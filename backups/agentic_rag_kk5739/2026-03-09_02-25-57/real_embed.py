"""
Real semantic embeddings for text chunks using BGE (sentence-transformers).

Inputs: data/chunks.jsonl, data/linked_chunks.jsonl
Output: data/real_vectors.jsonl
"""
from __future__ import annotations

import sys
import os as _os

# venv site-packages 최우선 (시스템 typing_extensions 등과 충돌 방지)
_here = _os.path.dirname(_os.path.abspath(__file__))
_venv_site = _os.path.join(_here, ".venv", "lib", "python3.10", "site-packages")
if _os.path.isdir(_venv_site):
    if _venv_site not in sys.path:
        sys.path.insert(0, _venv_site)
    _sys_site = _os.path.join(_os.path.sep + "gpfs", "share", "apps", "python")
    sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

import json
import math
import os
from typing import Dict, List

CHUNKS_JSONL = "data/chunks.jsonl"
LINKED_CHUNKS_JSONL = "data/linked_chunks.jsonl"
REAL_VECTORS_JSONL = "data/real_vectors.jsonl"
DEFAULT_MODEL = "BAAI/bge-base-en-v1.5"
# GPU 있으면 배치 크기 키우면 속도 대폭 상승 (예: 32~64). CPU/메모리 적으면 1~8 유지.
DEFAULT_BATCH_SIZE = 1


def _l2_normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in vec))
    return [x / n for x in vec] if n > 0 else vec


def _load_linked(path: str) -> Dict[str, Dict]:
    linked: Dict[str, Dict] = {}
    if not os.path.isfile(path):
        return linked
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            linked[rec["chunk_id"]] = {
                "doc_id": rec["doc_id"],
                "parent_block_id": rec["parent_block_id"],
                "modality": rec["modality"],
            }
    return linked


def main() -> None:
    model_name = os.environ.get("EMBED_MODEL", DEFAULT_MODEL)
    try:
        batch_size = int(os.environ.get("BATCH_SIZE", str(DEFAULT_BATCH_SIZE)))
    except ValueError:
        batch_size = DEFAULT_BATCH_SIZE
    batch_size = max(1, batch_size)

    # GPU 사용 시 속도 크게 향상. CPU만 있으면 DEVICE=cpu 또는 미설정.
    import torch

    device_env = os.environ.get("DEVICE", "").lower()
    if device_env:
        device = device_env if device_env in ("cuda", "cpu", "mps") else "cpu"
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and batch_size == 1:
        print(
            "Hint: GPU 사용 중입니다. 속도 향상을 위해 BATCH_SIZE=32 또는 64 시도 "
            "(예: BATCH_SIZE=32 .venv/bin/python real_embed.py)",
            flush=True,
        )

    linked = _load_linked(LINKED_CHUNKS_JSONL)

    # Incremental: 이미 임베딩된 chunk_id는 스킵
    existing_vector_chunk_ids: set[str] = set()
    existing_vector_rows: List[Dict] = []
    incremental = os.environ.get("INCREMENTAL", "").lower() in ("1", "true", "yes")
    if incremental and os.path.isfile(REAL_VECTORS_JSONL):
        with open(REAL_VECTORS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                existing_vector_chunk_ids.add(row["chunk_id"])
                existing_vector_rows.append(row)
        if existing_vector_chunk_ids:
            print(
                f"Incremental: {len(existing_vector_chunk_ids)} existing vector(s), "
                "embedding new text chunks only.",
                flush=True,
            )

    # linked에 존재하고, text가 비어 있지 않고, (증분 모드면) 아직 임베딩 안 된 text 청크만 모으기
    chunks_to_embed: List[Dict] = []
    skipped = 0
    if not os.path.isfile(CHUNKS_JSONL):
        print(f"{CHUNKS_JSONL} not found.")
        raise SystemExit(1)
    with open(CHUNKS_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            if chunk.get("modality") != "text":
                skipped += 1
                continue
            text = (chunk.get("text") or "").strip()
            if not text:
                skipped += 1
                continue
            cid = chunk["chunk_id"]
            if cid not in linked:
                skipped += 1
                continue
            if incremental and cid in existing_vector_chunk_ids:
                skipped += 1
                continue
            chunks_to_embed.append(chunk)

    if not chunks_to_embed:
        print("No chunks to embed.")
        print(f"Skipped: {skipped}")
        print(f"Output: {REAL_VECTORS_JSONL}")
        return

    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer

    print(f"Loading model '{model_name}' on device={device}...", flush=True)
    model = SentenceTransformer(model_name, device=device)

    texts = ["passage: " + (c.get("text") or "") for c in chunks_to_embed]
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=True,
    )

    os.makedirs(os.path.dirname(REAL_VECTORS_JSONL) or ".", exist_ok=True)
    all_rows: List[Dict] = list(existing_vector_rows)
    for chunk, vec in zip(chunks_to_embed, vectors):
        if hasattr(vec, "tolist"):
            vec = vec.tolist()
        vec = _l2_normalize(list(vec))
        cid = chunk["chunk_id"]
        meta = linked[cid]
        all_rows.append(
            {
                "chunk_id": cid,
                "doc_id": meta["doc_id"],
                "parent_block_id": meta["parent_block_id"],
                "modality": meta["modality"],
                "vector": vec,
            }
        )

    with open(REAL_VECTORS_JSONL, "w", encoding="utf-8") as out:
        for row in all_rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Embedded: {len(chunks_to_embed)} (total vectors: {len(all_rows)})")
    print(f"Skipped: {skipped}")
    print(f"Output: {REAL_VECTORS_JSONL}")


if __name__ == "__main__":
    main()

