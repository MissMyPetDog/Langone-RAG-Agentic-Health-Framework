"""
Chunk text/table/image blocks into retrieval units.

Inputs: data/blocks.jsonl
Output: data/chunks.jsonl

텍스트:
- 문장 단위로 나눈 뒤, 문자 수 기준 슬라이딩 윈도우 (TARGET_CHARS, OVERLAP_CHARS).
테이블/이미지:
- 1 block = 1 chunk (페이지/asset_path 유지).
"""
from __future__ import annotations

import sys
import os as _os

# venv site-packages 최우선
_here = _os.path.dirname(_os.path.abspath(__file__))
_venv_site = _os.path.join(_here, ".venv", "lib", "python3.10", "site-packages")
if _os.path.isdir(_venv_site):
    if _venv_site not in sys.path:
        sys.path.insert(0, _venv_site)
    _sys_site = _os.path.join(_os.path.sep + "gpfs", "share", "apps", "python")
    sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

import json
import os
import re
from typing import Dict, Iterable, List

BLOCKS_JSONL = "data/blocks.jsonl"
CHUNKS_JSONL = "data/chunks.jsonl"

TARGET_CHARS = 1200
OVERLAP_CHARS = 200
# 한 블록 텍스트 최대 길이 (초과 시 잘라서 처리 → OOM 방지). 메모리 부족 시 MAX_BLOCK_CHARS=100000 등으로 낮추기
MAX_BLOCK_CHARS = int(os.environ.get("MAX_BLOCK_CHARS", "300000"))


def _iter_blocks(path: str) -> Iterable[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _split_sentences(text: str) -> List[str]:
    """단순 문장 분리: .?! 뒤 공백 기준."""
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[\.!?])\s+", text)
    out = [p.strip() for p in parts if p.strip()]
    return out


def _sliding_windows(sentences: List[str]) -> Iterable[str]:
    """Yield one window at a time to avoid holding all in memory."""
    if not sentences:
        return
    start = 0
    n = len(sentences)
    while start < n:
        cur = []
        length = 0
        i = start
        while i < n and length < TARGET_CHARS:
            s = sentences[i]
            cur.append(s)
            length += len(s) + 1
            i += 1
        if not cur:
            break
        # 한 문장이 TARGET_CHARS보다 길면 그대로 한 청크로 (그렇지 않으면 start가 안 늘어나 무한 루프)
        chunk_text = " ".join(cur).strip()
        yield chunk_text
        overlap_len = 0
        j = i - 1
        while j > start and overlap_len < OVERLAP_CHARS:
            overlap_len += len(sentences[j]) + 1
            j -= 1
        next_start = max(j, 0)
        # 진행이 없으면 무한 루프 방지: 최소 1칸 전진
        if next_start <= start:
            next_start = i
        start = next_start
        if start >= n:
            break


def _chunk_text_block(block: Dict) -> Iterable[Dict]:
    """Yield one chunk record at a time (low memory)."""
    text = (block.get("text") or "").strip()
    if not text:
        return
    if len(text) > MAX_BLOCK_CHARS:
        print(f"Warning: block {block.get('block_id')} text truncated ({len(text)} -> {MAX_BLOCK_CHARS} chars)", flush=True)
        text = text[:MAX_BLOCK_CHARS]
    sentences = _split_sentences(text)
    doc_id = block["doc_id"]
    block_id = block["block_id"]
    page = block.get("page")
    for idx, win in enumerate(_sliding_windows(sentences)):
        chunk_id = f"{block_id}_c{idx}"
        rec: Dict = {
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "block_id": block_id,
            "modality": "text",
            "text": win,
        }
        if page is not None:
            rec["page"] = page
        yield rec


def _chunk_non_text_block(block: Dict) -> Dict:
    doc_id = block["doc_id"]
    block_id = block["block_id"]
    modality = block["modality"]
    page = block.get("page")
    asset_path = block.get("asset_path")
    chunk_id = f"{block_id}_c0"
    rec: Dict = {
        "chunk_id": chunk_id,
        "doc_id": doc_id,
        "block_id": block_id,
        "modality": modality,
    }
    if page is not None:
        rec["page"] = page
    if asset_path:
        rec["asset_path"] = asset_path
    text = (block.get("text") or "").strip()
    if text:
        rec["text"] = text
    return rec


def main() -> None:
    if not os.path.isfile(BLOCKS_JSONL):
        print(f"{BLOCKS_JSONL} not found.")
        raise SystemExit(1)

    os.makedirs(os.path.dirname(CHUNKS_JSONL) or ".", exist_ok=True)
    count = 0
    with open(CHUNKS_JSONL, "w", encoding="utf-8") as out:
        for block in _iter_blocks(BLOCKS_JSONL):
            modality = block.get("modality")
            if modality == "text":
                for rec in _chunk_text_block(block):
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    count += 1
            elif modality in ("image", "table"):
                rec = _chunk_non_text_block(block)
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

    print(f"Wrote {count} chunks to {CHUNKS_JSONL}")


if __name__ == "__main__":
    main()

