"""
멀티모달 임베딩: table + image 청크만 CLIP으로 임베딩.

텍스트는 real_embed.py (BGE) → real_vectors.jsonl.
이 스크립트 → data/vectors_multimodal.jsonl (텍스트 DB와 parent_block_id로 연동).

환경 변수: MULTIMODAL_IMAGE_LIMIT (양의 정수) — 이미지를 이 개수만 인코딩한 뒤 종료. CPU 세션 제한 회피용.
"""
from __future__ import annotations

import sys
import os as _os

# 프로젝트 .venv 우선; rag_venv만 path에서 제거 (torch/torchvision 섞임 방지)
_here = _os.path.dirname(_os.path.abspath(__file__))
_vi = sys.version_info
_venv_site = _os.path.join(
    _here, ".venv", "lib", f"python{_vi.major}.{_vi.minor}", "site-packages"
)


def _strip_conflicting_venv_paths() -> None:
    banned = ("rag_venv",)
    kept: list[str] = []
    for p in sys.path:
        if p == "":
            kept.append(p)
            continue
        norm = p.replace("\\", "/")
        if any(b in norm for b in banned):
            continue
        kept.append(p)
    sys.path[:] = kept


if _os.path.isdir(_venv_site):
    _strip_conflicting_venv_paths()
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
# image vec + OCR text vec 결합 비율 (0=이미지만, 1=텍스트만)
DEFAULT_OCR_FUSION_ALPHA = 0.35


def _l2_normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in vec))
    return [float(x) / n for x in vec] if n > 0 else list(vec)


def _fuse_vecs(image_vec: List[float], text_vec: List[float], alpha: float) -> List[float]:
    if alpha <= 0:
        return _l2_normalize(image_vec)
    if alpha >= 1:
        return _l2_normalize(text_vec)
    out = [(1.0 - alpha) * iv + alpha * tv for iv, tv in zip(image_vec, text_vec)]
    return _l2_normalize(out)


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
    try:
        ocr_alpha = float(os.environ.get("OCR_CLIP_FUSION_ALPHA", str(DEFAULT_OCR_FUSION_ALPHA)))
    except ValueError:
        ocr_alpha = DEFAULT_OCR_FUSION_ALPHA
    ocr_alpha = max(0.0, min(1.0, ocr_alpha))
    try:
        image_limit = max(0, int(os.environ.get("MULTIMODAL_IMAGE_LIMIT", "0")))
    except ValueError:
        image_limit = 0
    # image_limit>0 이면 이미지 인코딩을 이 개수만큼만 하고 종료 (CPU 세션 시간 제한 회피 후 재실행)

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
    print(f"OCR+CLIP fusion alpha={ocr_alpha:.2f}", flush=True)
    model = SentenceTransformer(model_name, device=device)

    all_rows: List[Dict] = list(existing_vector_rows)

    def _flush_multimodal_jsonl() -> None:
        os.makedirs(os.path.dirname(VECTORS_MULTIMODAL_JSONL) or ".", exist_ok=True)
        with open(VECTORS_MULTIMODAL_JSONL, "w", encoding="utf-8") as out:
            for row in all_rows:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")

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

    n_new = 0

    # Table 배치
    if table_chunks:
        texts = [(c.get("text") or "").strip()[:4000] for c in table_chunks]
        table_vecs = _batched_encode_text(texts)
        for chunk, vec in zip(table_chunks, table_vecs):
            cid = chunk["chunk_id"]
            meta = linked[cid]
            all_rows.append(
                {
                    "chunk_id": cid,
                    "doc_id": meta["doc_id"],
                    "parent_block_id": meta["parent_block_id"],
                    "modality": meta["modality"],
                    "vector": _l2_normalize(vec),
                }
            )
            n_new += 1
        if incremental:
            _flush_multimodal_jsonl()

    # Image: 배치 단위로 인코딩 후 즉시 저장 (INCREMENTAL 시 장시간 CPU 작업 중단에도 진행분 유지)
    if image_chunks:
        image_ocr_texts = [(c.get("text") or "").strip()[:4000] for c in image_chunks]
        non_empty_idx = [i for i, t in enumerate(image_ocr_texts) if t]
        ocr_vec_by_idx: Dict[int, List[float]] = {}
        if non_empty_idx and ocr_alpha > 0:
            ocr_text_batch = [image_ocr_texts[i] for i in non_empty_idx]
            ocr_text_vecs = _batched_encode_text(ocr_text_batch)
            for i, v in zip(non_empty_idx, ocr_text_vecs):
                ocr_vec_by_idx[i] = _l2_normalize(v)

        n_img = len(image_chunks)
        images_done_this_run = 0
        for start in range(0, n_img, batch_size):
            sub = image_chunks[start : start + batch_size]
            paths = [c["asset_path"] for c in sub]
            image_vecs = _batched_encode_images(paths)
            for j, (chunk, vec) in enumerate(zip(sub, image_vecs)):
                if vec is None:
                    continue
                idx = start + j
                img_vec = _l2_normalize(vec)
                txt_vec = ocr_vec_by_idx.get(idx)
                if txt_vec is not None:
                    out_vec = _fuse_vecs(img_vec, txt_vec, ocr_alpha)
                else:
                    out_vec = img_vec
                cid = chunk["chunk_id"]
                meta = linked[cid]
                all_rows.append(
                    {
                        "chunk_id": cid,
                        "doc_id": meta["doc_id"],
                        "parent_block_id": meta["parent_block_id"],
                        "modality": meta["modality"],
                        "vector": out_vec,
                    }
                )
                n_new += 1
                images_done_this_run += 1
            if incremental:
                _flush_multimodal_jsonl()
            if image_limit > 0 and images_done_this_run >= image_limit:
                print(
                    f"Stopped after MULTIMODAL_IMAGE_LIMIT={image_limit} image(s); "
                    "re-run with same env to continue.",
                    flush=True,
                )
                break

    if not incremental:
        _flush_multimodal_jsonl()

    print(f"Multimodal embedded: {n_new} new (total: {len(all_rows)}) (table + image)")
    print(f"Output: {VECTORS_MULTIMODAL_JSONL}")


if __name__ == "__main__":
    main()

