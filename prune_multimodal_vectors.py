#!/usr/bin/env python3
"""vectors_multimodal.jsonl 정리: 유효하지 않은 chunk 제거, 또는 이미지 행만 제거(OCR 융합 재임베딩용)."""
from __future__ import annotations

import argparse
import json
import os

_here = os.path.dirname(os.path.abspath(__file__))
CHUNKS = os.path.join(_here, "data", "chunks.jsonl")
LINKED = os.path.join(_here, "data", "linked_chunks.jsonl")
VECTORS = os.path.join(_here, "data", "vectors_multimodal.jsonl")


def _need_chunk_ids() -> set[str]:
    linked: dict[str, str] = {}
    with open(LINKED, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            linked[r["chunk_id"]] = r["modality"]
    need: set[str] = set()
    with open(CHUNKS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            c = json.loads(line)
            cid = c.get("chunk_id")
            if not cid or cid not in linked:
                continue
            m = linked[cid]
            if m == "table" and (c.get("text") or "").strip():
                need.add(cid)
            elif m == "image" and c.get("asset_path"):
                ap = c["asset_path"]
                abs_p = ap if os.path.isabs(ap) else os.path.join(_here, ap)
                if os.path.isfile(abs_p):
                    need.add(cid)
    return need


def _strip_image_rows() -> None:
    if not os.path.isfile(VECTORS):
        print("No vectors file.")
        return
    kept: list[dict] = []
    with open(VECTORS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("modality") != "image":
                kept.append(r)
    tmp = VECTORS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, VECTORS)
    print(f"Removed image rows from {VECTORS}: {len(kept)} rows kept")


def _prune_stale() -> None:
    need = _need_chunk_ids()
    if not os.path.isfile(VECTORS):
        print("No vectors file to prune.")
        return
    kept: list[dict] = []
    with open(VECTORS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("chunk_id") in need:
                kept.append(r)
    tmp = VECTORS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, VECTORS)
    print(f"Pruned {VECTORS}: {len(kept)} rows (universe size {len(need)})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--strip-images",
        action="store_true",
        help="이미지 modality 행만 삭제 (테이블 벡터 유지, INCREMENTAL 재임베딩 전)",
    )
    args = p.parse_args()
    if args.strip_images:
        _strip_image_rows()
    else:
        _prune_stale()


if __name__ == "__main__":
    main()
