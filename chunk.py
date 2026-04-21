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

# 목차/표지 같은 저가치 chunk 제거 스위치 (기본 ON).
# OFF로 주고 싶으면 FILTER_TOC_CHUNKS=0 으로 설정.
FILTER_TOC_CHUNKS = os.environ.get("FILTER_TOC_CHUNKS", "1").lower() in ("1", "true", "yes")

# TOC entries typical markers (Chapter X.Y:, Section N:, Table/Figure N.)
# p13 같은 권고문에서 쓰는 "3.9.1:" 형태는 접두어 없이 숫자만 나오므로 매칭 안 됨.
_TOC_ENTRY_PATTERNS = [
    re.compile(r"\bChapter\s+\d+(?:\.\d+)+:", re.IGNORECASE),
    re.compile(r"\bSection\s+\d+:", re.IGNORECASE),
    re.compile(r"\bTable\s+\d+\.", re.IGNORECASE),
    re.compile(r"\bFigure\s+\d+\.", re.IGNORECASE),
    re.compile(r"\bAppendix\s+[A-Z]\b"),
]

# 표지·러닝헤드 류 짧은 chunk 시그너처
_BOILERPLATE_PATTERNS = [
    re.compile(r"\bVOL(?:UME)?\.?\s+\d+\s*\|\s*(?:ISSUE|SUPPLEMENT)\s+\d+", re.IGNORECASE),
    re.compile(r"OFFICIAL\s+JOURNAL\s+OF", re.IGNORECASE),
    re.compile(r"(?:©|&)\s*\d{4}\s+KDIGO", re.IGNORECASE),
    re.compile(r"\bISBN[-\s:]\s*\d", re.IGNORECASE),
    re.compile(r"\bKidney\s+International\s+Supplements?\b", re.IGNORECASE),
]

# Front-matter (서문/면책/디스클로저/바이오): 길이와 무관하게 2+ 히트면 드롭
# 실제 권고문에는 거의 등장 안 하는 표현들만 선별.
_FRONT_MATTER_PATTERNS = [
    re.compile(r"\bSECTION\s+[IVX]+\s*:", re.IGNORECASE),
    re.compile(r"\bUSE\s+OF\s+THE\s+CLINICAL\s+PRACTICE\s+GUIDELINE\b", re.IGNORECASE),
    re.compile(r"\bDISCLOSURE\b", re.IGNORECASE),
    re.compile(r"\bCONFLICTS?\s+OF\s+INTEREST\b", re.IGNORECASE),
    re.compile(r"\bBiographical\s+and\s+Disclosure\b", re.IGNORECASE),
    re.compile(r"\bWork\s+Group(?:\s+Members?hip)?\b", re.IGNORECASE),
    re.compile(r"\bReference\s+Keys?\b", re.IGNORECASE),
    re.compile(r"\bAcknowledg(?:e?ments?)\b", re.IGNORECASE),
    re.compile(r"\bAbbreviations\s+and\s+Acronyms\b", re.IGNORECASE),
    re.compile(r"\bForeword\b", re.IGNORECASE),
    re.compile(r"\bdoi:\s*10\.", re.IGNORECASE),
]


def _looks_like_toc_or_boilerplate(text: str) -> bool:
    """Heuristic: True if chunk is a TOC-style listing or a cover/running-header line."""
    t = (text or "").strip()
    if not t:
        return True

    # 1) 짧은 표지/러닝헤드류. 단, 실제 권고문에 푸터 한 줄이 붙어 들어온 케이스
    #    (예: "... (1A). This will usually ... 12 Kidney International Supplements (2012)")
    #    는 살려야 하므로, 매칭 비율이 유의미할 때만 드롭.
    if len(t) < 400:
        bp_hit_count = 0
        bp_match_len = 0
        for p in _BOILERPLATE_PATTERNS:
            for m in p.finditer(t):
                bp_hit_count += 1
                bp_match_len += m.end() - m.start()
        if bp_hit_count >= 2:
            # 한 chunk에 표지/퍼블리셔 시그너처 2종 이상 → 표지급
            return True
        if bp_hit_count == 1:
            remaining = len(t) - bp_match_len
            if bp_match_len / len(t) > 0.4 or remaining < 80:
                return True

    # 2) TOC 엔트리 밀도 (길이 무관)
    toc_hits = sum(len(p.findall(t)) for p in _TOC_ENTRY_PATTERNS)
    if toc_hits >= 4:
        # 1000자당 3회 이상이면 TOC로 간주
        density = toc_hits / max(len(t) / 1000.0, 1.0)
        if density >= 3.0:
            return True

    # 3) Front-matter: Notice / Disclosure / Use of Guideline / Work Group 류
    #    한 chunk에 서로 다른 front-matter signature가 2개 이상 등장하면 본문 아님으로 간주.
    fm_hits = sum(1 for p in _FRONT_MATTER_PATTERNS if p.search(t))
    if fm_hits >= 2:
        return True

    return False


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


def _chunk_text_block(block: Dict, drop_stats: Dict[str, int] | None = None) -> Iterable[Dict]:
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
    idx_out = 0
    for win in _sliding_windows(sentences):
        if FILTER_TOC_CHUNKS and _looks_like_toc_or_boilerplate(win):
            if drop_stats is not None:
                drop_stats["toc"] = drop_stats.get("toc", 0) + 1
            continue
        chunk_id = f"{block_id}_c{idx_out}"
        idx_out += 1
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
    drop_stats: Dict[str, int] = {}
    with open(CHUNKS_JSONL, "w", encoding="utf-8") as out:
        for block in _iter_blocks(BLOCKS_JSONL):
            modality = block.get("modality")
            if modality == "text":
                for rec in _chunk_text_block(block, drop_stats):
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    count += 1
            elif modality in ("image", "table"):
                rec = _chunk_non_text_block(block)
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

    print(f"Wrote {count} chunks to {CHUNKS_JSONL}")
    if FILTER_TOC_CHUNKS and drop_stats.get("toc"):
        print(f"  [FILTER_TOC_CHUNKS=1] Dropped {drop_stats['toc']} TOC/boilerplate chunk(s). Set FILTER_TOC_CHUNKS=0 to keep them.")


if __name__ == "__main__":
    main()

