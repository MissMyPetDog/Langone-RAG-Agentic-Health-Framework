"""
멀티모달 임베딩: table + image 청크만 CLIP으로 임베딩.

텍스트는 real_embed.py (BGE) → real_vectors.jsonl.
이 스크립트 → data/vectors_multimodal.jsonl (텍스트 DB와 parent_block_id로 연동).
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
VECTORS_MULTIMODAL_JSONL = "data/vectors_multimodal.jsonl"
DEFAULT_MODEL = "clip-ViT-B-32"
# 이미지/테이블 한 번에 묶어서 인코딩. GPU 메모리 적으면 8, 넉넉하면 16~32.
DEFAULT_BATCH_SIZE = 16


def _l2_normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in vec))
    return [float(x) / n for x in vec] if n > 0 else list(vec)


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
    model_name = os.environ.get("MULTIMODAL_EMBED_MODEL", DEFAULT_MODEL)
    try:
        batch_size = max(1, int(os.environ.get("BATCH_SIZE", str(DEFAULT_BATCH_SIZE))))
    except ValueError:
        batch_size = DEFAULT_BATCH_SIZE

    import torch

    device_env = os.environ.get("DEVICE", "").lower()
    if device_env:
        device = device_env if device_env in ("cuda", "cpu", "mps") else "cpu"
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    linked = _load_linked(LINKED_CHUNKS_JSONL)

    existing_vector_chunk_ids: set[str] = set()
    existing_vector_rows: List[Dict] = []
    incremental = os.environ.get("INCREMENTAL", "").lower() in ("1", "true", "yes")
    if incremental and os.path.isfile(VECTORS_MULTIMODAL_JSONL):
        with open(VECTORS_MULTIMODAL_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                existing_vector_chunk_ids.add(row["chunk_id"])
                existing_vector_rows.append(row)
        if existing_vector_chunk_ids:
            print(
                f"Incremental: {len(existing_vector_chunk_ids)} existing multimodal vector(s), "
                "embedding new only.",
                flush=True,
            )

    table_chunks: List[Dict] = []
    image_chunks: List[Dict] = []
    if not os.path.isfile(CHUNKS_JSONL):
        print(f"{CHUNKS_JSONL} not found.")
        raise SystemExit(1)
    with open(CHUNKS_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            cid = chunk.get("chunk_id")
            if not cid or cid not in linked:
                continue
            if incremental and cid in existing_vector_chunk_ids:
                continue
            modality = chunk.get("modality")
            if modality == "table" and (chunk.get("text") or "").strip():
                table_chunks.append(chunk)
            elif modality == "image" and chunk.get("asset_path") and os.path.isfile(chunk["asset_path"]):
                image_chunks.append(chunk)

    to_embed = table_chunks + image_chunks
    if not to_embed:
        print("No table or image chunks to embed.")
        print(f"Output: {VECTORS_MULTIMODAL_JSONL}")
        return

    from sentence_transformers import SentenceTransformer
    from PIL import Image

    print(f"Loading CLIP model '{model_name}' on device={device}...", flush=True)
    model = SentenceTransformer(model_name, device=device)

    def _batched_encode_text(texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vecs = model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=len(texts) > batch_size,
        )
        out: List[List[float]] = []
        for v in vecs:
            if hasattr(v, "tolist"):
                v = v.tolist()
            out.append(list(v))
        return out

    def _batched_encode_images(paths: List[str]) -> List[List[float] | None]:
        if not paths:
            return []
        imgs = []
        for p in paths:
            try:
                imgs.append(Image.open(p).convert("RGB"))
            except Exception:
                imgs.append(None)
        valid_idx = [i for i, img in enumerate(imgs) if img is not None]
        if not valid_idx:
            return [None] * len(paths)
        batch_imgs = [imgs[i] for i in valid_idx]
        vecs = model.encode(
            batch_imgs,
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=len(batch_imgs) > batch_size,
        )
        out: List[List[float] | None] = [None] * len(paths)
        for idx, v in zip(valid_idx, vecs):
            if hasattr(v, "tolist"):
                v = v.tolist()
            out[idx] = list(v)
        return out

    vectors_list: List[tuple[Dict, List[float]]] = []

    # Table 배치
    if table_chunks:
        texts = [(c.get("text") or "").strip()[:4000] for c in table_chunks]
        table_vecs = _batched_encode_text(texts)
        for chunk, vec in zip(table_chunks, table_vecs):
            vectors_list.append((chunk, _l2_normalize(vec)))

    # Image 배치
    if image_chunks:
        paths = [c["asset_path"] for c in image_chunks]
        image_vecs = _batched_encode_images(paths)
        for chunk, vec in zip(image_chunks, image_vecs):
            if vec is None:
                continue
            vectors_list.append((chunk, _l2_normalize(vec)))

    os.makedirs(os.path.dirname(VECTORS_MULTIMODAL_JSONL) or ".", exist_ok=True)
    all_rows: List[Dict] = list(existing_vector_rows)
    for chunk, vec in vectors_list:
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

    with open(VECTORS_MULTIMODAL_JSONL, "w", encoding="utf-8") as out:
        for row in all_rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Multimodal embedded: {len(vectors_list)} new (total: {len(all_rows)}) (table + image)")
    print(f"Output: {VECTORS_MULTIMODAL_JSONL}")


if __name__ == "__main__":
    main()

