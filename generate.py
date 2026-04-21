"""
End-to-end QA:
- Retrieve context from real_vectors (BGE) and chunks/linked_chunks
- Call an LLM via OpenAI API to answer using ONLY that context.
- Optional --vision: attach figure PNG/JPEG as image_url (model sees pixels), not CLIP vectors.
- Used Sources embeds only helpful figures: cited in sibling text/table for that parent, or substantive OCR
  (not every image on the same page). Set ALL_RETRIEVED_IMAGES=1 to embed all again. Optional:
  USED_SOURCES_IMAGE_MIN_OCR (default 90).
"""
from __future__ import annotations

import sys
import os as _os

# venv site-packages 최우선 (시스템 typing_extensions 충돌 방지)
_here = _os.path.dirname(_os.path.abspath(__file__))
_venv_site = _os.path.join(_here, ".venv", "lib", "python3.10", "site-packages")
if _os.path.isdir(_venv_site):
    if _venv_site not in sys.path:
        sys.path.insert(0, _venv_site)
    _sys_site = _os.path.join(_os.path.sep + "gpfs", "share", "apps", "python")
    sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

import os
from dotenv import load_dotenv

# Load .env variables on startup
load_dotenv()

import argparse
import base64
import heapq
import json
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Set, Tuple

from openai import OpenAI

ChunkRecord = Dict[str, Any]

LINKED_CHUNKS_JSONL = "data/linked_chunks.jsonl"
CHUNKS_JSONL = "data/chunks.jsonl"
REAL_VECTORS_JSONL = "data/real_vectors.jsonl"
VECTORS_JSONL = "data/vectors.jsonl"
PAPERS_JSONL = "papers.jsonl"
DEFAULT_VECTORS_JSONL = REAL_VECTORS_JSONL  # main에서 real 없으면 vectors 사용
BGE_MODEL = "BAAI/bge-base-en-v1.5"
MAX_CONTEXT_TOKENS = 1500
CHARS_PER_TOKEN = 4  # rough heuristic for truncation

# Initialize OpenAI client with KONG_API_KEY (NYUMC Kong)
openai_api_key = os.getenv("KONG_API_KEY")
client = OpenAI(
    base_url="https://kong-api.prod1.nyumc.org/gpt-4o/v1.3.0",
    api_key=openai_api_key,
    default_headers={"api-key": openai_api_key},
)


def _embed_query_bge(query: str) -> List[float]:
    # 오프라인 미설정 시 온라인 허용 (캐시 없을 때 BGE 다운로드)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("sentence-transformers is not installed. Install with:")
        print("  pip install -U sentence-transformers torch")
        raise SystemExit(1)

    import time
    model_name = os.environ.get("EMBED_MODEL", BGE_MODEL)
    print(f"Loading BGE model '{model_name}' (takes ~10s on cold load)...", flush=True)
    t0 = time.time()
    model = SentenceTransformer(model_name)
    print(f"Model loaded in {time.time() - t0:.1f}s", flush=True)
    query_text = "query: " + query
    vec = model.encode([query_text], normalize_embeddings=True)[0]
    n = math.sqrt(sum(x * x for x in vec))
    if n > 0:
        vec = [float(x) / n for x in vec]
    else:
        vec = vec.tolist() if hasattr(vec, "tolist") else list(vec)
    return vec


def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _load_linked(path: str) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["chunk_id"]] = {
                "doc_id": rec["doc_id"],
                "parent_block_id": rec["parent_block_id"],
                "modality": rec["modality"],
            }
    return out


def _load_linked_by_parents(path: str, parent_ids: Set[str]) -> Dict[str, List[str]]:
    """Stream linked_chunks; build by_parent only for given parent_ids (low memory)."""
    by_parent: Dict[str, List[str]] = {pid: [] for pid in parent_ids}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            pid = rec.get("parent_block_id")
            if pid in by_parent:
                by_parent[pid].append(rec["chunk_id"])
    return by_parent


def _load_chunk_records_for_ids(path: str, chunk_ids: Set[str]) -> Dict[str, ChunkRecord]:
    """Load modality, text, asset_path for chunk_ids (stream, low memory)."""
    out: Dict[str, ChunkRecord] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cid = rec.get("chunk_id")
            if cid in chunk_ids:
                out[cid] = {
                    "modality": (rec.get("modality") or "text").strip(),
                    "text": (rec.get("text") or "").strip(),
                    "asset_path": (rec.get("asset_path") or "").strip(),
                }
    return out


def _parent_text_for_rerank(cids: List[str], chunk_records: Dict[str, ChunkRecord]) -> str:
    parts: List[str] = []
    for cid in cids:
        rec = chunk_records.get(cid)
        if not rec:
            continue
        mod = rec.get("modality") or "text"
        if mod == "text":
            t = rec.get("text") or ""
            if t:
                parts.append(t)
        elif mod == "table":
            t = rec.get("text") or ""
            if t:
                parts.append(t)
        elif mod == "image":
            ap = rec.get("asset_path") or ""
            t = rec.get("text") or ""
            if ap:
                parts.append(f"[image file: {_prefer_png_asset_path_if_exists(ap.strip())}]")
            if t:
                parts.append(f"[image OCR]\n{t}")
    return "\n\n".join(parts).strip()


def _format_parent_content_for_llm(
    cids: List[str],
    chunk_records: Dict[str, ChunkRecord],
    include_image_chunks: bool = True,
) -> str:
    parts: List[str] = []
    for cid in cids:
        rec = chunk_records.get(cid)
        if not rec:
            continue
        mod = rec.get("modality") or "text"
        if mod == "image":
            if not include_image_chunks:
                continue
            ap = rec.get("asset_path") or ""
            t = rec.get("text") or ""
            ap_show = _prefer_png_asset_path_if_exists(ap.strip()) if ap else ""
            if ap_show:
                if t:
                    parts.append(f"[Image chunk {cid}]\nasset_path: {ap_show}\nocr_text:\n{t}")
                else:
                    parts.append(f"[Image chunk {cid}]\nasset_path: {ap_show}")
            else:
                if t:
                    parts.append(f"[Image chunk {cid}] (no asset_path)\nocr_text:\n{t}")
                else:
                    parts.append(f"[Image chunk {cid}] (no asset_path)")
        elif mod == "table":
            t = rec.get("text") or ""
            if t:
                parts.append(f"[Table chunk {cid}]\n{t}")
        else:
            t = rec.get("text") or ""
            if t:
                parts.append(t)
    return "\n\n".join(parts).strip()


def _abs_project_path(p: str) -> str:
    if not p:
        return ""
    if os.path.isabs(p):
        return os.path.normpath(p)
    return os.path.normpath(os.path.join(_here, p))


def _prefer_png_asset_path_if_exists(asset_path: str) -> str:
    """chunks에 .jpx 등이 남아 있어도 같은 stem의 .png가 있으면 그 경로를 쓴다 (미리보기·LLM 텍스트)."""
    ap = (asset_path or "").strip()
    if not ap:
        return ap
    ext = os.path.splitext(ap)[1].lower()
    stem = ap[: -len(ext)] if ext else ap
    png_rel = stem + ".png"
    if os.path.isfile(_abs_project_path(png_rel)):
        return png_rel
    return ap


def _include_all_retrieved_images() -> bool:
    return os.environ.get("ALL_RETRIEVED_IMAGES", "").lower() in ("1", "true", "yes")


def _sibling_text_table_corpus(
    cids: List[str], chunk_records: Dict[str, ChunkRecord], skip_cid: str | None = None
) -> str:
    """Same-parent text + table chunks (no image OCR) for figure-citation matching."""
    parts: List[str] = []
    for xid in cids:
        if skip_cid is not None and xid == skip_cid:
            continue
        rec = chunk_records.get(xid) or {}
        mod = (rec.get("modality") or "text").strip()
        if mod == "image":
            continue
        t = (rec.get("text") or "").strip()
        if t:
            parts.append(t)
    return "\n".join(parts)


def _fig_number_from_image_chunk(cid: str, asset_path: str) -> int | None:
    for s in (cid or "", asset_path or ""):
        m = re.search(r"(?i)fig_(\d+)", s)
        if m:
            return int(m.group(1))
    return None


def _corpus_mentions_figure(fig_idx: int, corpus: str) -> bool:
    """True if sibling text likely refers to this figure index (tries N and N+1 for 0-based filenames)."""
    if fig_idx < 0 or not corpus:
        return False
    c = corpus.lower()
    candidates = {fig_idx, fig_idx + 1}
    for n in sorted(candidates):
        if n < 1:
            continue
        if re.search(rf"\bfigure\s*{n}\b", c):
            return True
        if re.search(rf"\bfig\.?\s*{n}\b", c):
            return True
        if re.search(rf"\bfigures?\s*{n}\b", c):
            return True
    return False


def _ocr_is_substantive_for_embed(ocr: str, min_len: int) -> bool:
    """Filter masthead/logo OCR and very short captions; keep text-heavy figures."""
    t = (ocr or "").strip()
    if len(t) < min_len:
        return False
    lower_ratio = sum(1 for ch in t if ch.islower()) / max(len(t), 1)
    if len(t) < 220 and lower_ratio < 0.04:
        return False
    if len(t) < 160 and not re.search(r"\d", t):
        return bool(re.search(r"\b(vs|patient|mg|ml|day|week|risk|use|recommend|therapy|treatment)\b", t, re.I))
    return True


def _image_worth_embedding_in_report(
    cid: str,
    rec: ChunkRecord,
    sibling_corpus: str,
) -> bool:
    """Used Sources / vision: not 'same page therefore include' — cite or substantive OCR."""
    if _include_all_retrieved_images():
        return True
    ocr = (rec.get("text") or "").strip()
    ap = (rec.get("asset_path") or "").strip()
    fig_n = _fig_number_from_image_chunk(cid, ap)
    if fig_n is not None and _corpus_mentions_figure(fig_n, sibling_corpus):
        return True
    try:
        min_ocr = max(20, int(os.environ.get("USED_SOURCES_IMAGE_MIN_OCR", "90")))
    except ValueError:
        min_ocr = 90
    return _ocr_is_substantive_for_embed(ocr, min_ocr)


# VS Code / GitHub 등 일반 MD 미리보기가 잘 여는 확장자 (JPEG2000 .jpx 등은 보통 미지원 → 깨진 이미지로 보임)
_MARKDOWN_PREVIEW_IMAGE_EXT = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"})
# Used Sources: JPEG2000는 미리보기에 쓰지 않고, 동일 stem의 PNG가 있을 때만 ![...]() 로 넣음
_JP2_FAMILY_EXT = frozenset({".jpx", ".jp2", ".j2k"})


def _markdown_image_line(asset_path: str, out_md_path: str) -> str:
    abs_img = _abs_project_path(asset_path)
    if not os.path.isfile(abs_img):
        return f"*(image not found on disk: `{asset_path}`)*"
    out_dir = os.path.dirname(out_md_path)
    rel = os.path.relpath(abs_img, start=out_dir)
    rel = rel.replace(os.sep, "/")
    base = os.path.basename(asset_path)
    ext = os.path.splitext(base)[1].lower()
    proj_rel = asset_path.replace(os.sep, "/")
    if ext in _MARKDOWN_PREVIEW_IMAGE_EXT:
        return f"![{base}]({rel})"
    return (
        f"*(Figure `{base}` — many Markdown previews cannot render `{ext}`; open the path below in an image/PDF viewer.)*\n\n"
        f"- Relative to this report: `{rel}`\n"
        f"- Under project root: `{proj_rel}`\n"
    )


def _used_sources_image_markdown(asset_path: str, out_md_path: str) -> str:
    """Used Sources: 디스크에 stem.png가 있으면 항상 그걸로 ![...]() (chunk가 .jpx를 가리켜도 동일)."""
    ap0 = (asset_path or "").strip()
    if not ap0:
        return "*(no asset_path)*"
    ap_png = _prefer_png_asset_path_if_exists(ap0)
    if ap_png.lower().endswith(".png") and os.path.isfile(_abs_project_path(ap_png)):
        return _markdown_image_line(ap_png, out_md_path)
    ext0 = os.path.splitext(ap0)[1].lower()
    if ext0 in _JP2_FAMILY_EXT:
        stem = ap0[: -len(ext0)] if ext0 else ap0
        png_proj = (stem + ".png").replace(os.sep, "/")
        proj = ap0.replace(os.sep, "/")
        return (
            f"*(JPEG2000 `{proj}` — Used Sources에는 PNG만 미리보기로 붙입니다; "
            f"`{png_proj}` 가 없어 embed 생략.)*\n\n"
            f"- 원본(외부 뷰어): `{proj}`\n"
        )
    return _markdown_image_line(ap0, out_md_path)


def _format_used_source_markdown(
    pid: str,
    doc_id: str,
    title: str,
    cids: List[str],
    chunk_records: Dict[str, ChunkRecord],
    out_md_path: str,
) -> str:
    if title:
        header = f"=== DOC {doc_id} / {title} / {pid} ==="
    else:
        header = f"=== DOC {doc_id} / {pid} ==="
    blocks: List[str] = [f"### {header}\n"]
    sibling_corpus = _sibling_text_table_corpus(cids, chunk_records)
    for cid in cids:
        rec = chunk_records.get(cid)
        if not rec:
            continue
        mod = rec.get("modality") or "text"
        if mod == "image":
            ap = rec.get("asset_path") or ""
            t = rec.get("text") or ""
            if not _image_worth_embedding_in_report(cid, rec, sibling_corpus):
                continue
            blocks.append(f"**`{cid}`** *(image)*\n")
            if ap:
                blocks.append(_used_sources_image_markdown(ap, out_md_path))
                blocks.append("")
            else:
                blocks.append("*(no asset_path)*\n")
            if t:
                blocks.append("**OCR text**\n")
                blocks.append("```\n" + t + "\n```\n")
        elif mod == "table":
            t = rec.get("text") or ""
            blocks.append(f"**`{cid}`** *(table)*\n")
            blocks.append("```\n" + (t if t else "[empty]") + "\n```\n")
        else:
            t = rec.get("text") or ""
            if t:
                blocks.append(f"**`{cid}`** *(text)*\n\n{t}\n")
    # Skip parents where nothing but the header survived (e.g. all images got filtered out)
    if len(blocks) <= 1:
        return ""
    body = "\n".join(blocks).strip()
    return body + "\n\n"


def _stream_vectors_topk(
    path: str, qvec: List[float], stage1_k: int
) -> List[Tuple[str, str, str, float]]:
    """Stream vectors file; keep only top stage1_k by score (avoids loading all into memory).
    Returns list of (chunk_id, doc_id, parent_block_id, score) sorted by score desc.
    """
    heap: List[Tuple[float, str, str, str]] = []  # (neg_score, chunk_id, doc_id, parent_block_id)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            score = _dot(qvec, row["vector"])
            item = (-score, row["chunk_id"], row["doc_id"], row["parent_block_id"])
            if len(heap) < stage1_k:
                heapq.heappush(heap, item)
            elif score > -heap[0][0]:
                heapq.heapreplace(heap, item)
    out = [(cid, doc_id, pid, -neg_s) for neg_s, cid, doc_id, pid in heap]
    out.sort(key=lambda x: -x[3])
    return out


def _load_papers_meta(path: str = PAPERS_JSONL) -> Dict[str, Dict[str, str]]:
    """doc_id -> {title, source} 매핑 로드 (없으면 빈 dict)."""
    meta: Dict[str, Dict[str, str]] = {}
    if not os.path.isfile(path):
        return meta
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            doc_id = rec.get("doc_id")
            if not doc_id:
                continue
            title = (rec.get("title") or "").strip()
            source = (rec.get("source") or "").strip()
            meta[doc_id] = {"title": title, "source": source}
    return meta


def _linked_to_by_parent(linked: Dict[str, Dict]) -> Dict[str, List[str]]:
    """parent_block_id -> [chunk_ids] for all chunks (text + table + image)."""
    by_parent: Dict[str, List[str]] = {}
    for cid, meta in linked.items():
        pid = meta["parent_block_id"]
        if pid not in by_parent:
            by_parent[pid] = []
        by_parent[pid].append(cid)
    return by_parent


def _load_chunk_texts(path: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["chunk_id"]] = (rec.get("text") or "").strip()
    return out


def _load_vectors(path: str) -> List[Dict]:
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _chunk_index(chunk_id: str) -> int:
    """Extract _cN from chunk_id for ordering (e.g. xxx_p1_c2 -> 2)."""
    m = re.search(r"_c(\d+)$", chunk_id)
    return int(m.group(1)) if m else 0


def _truncate_tokens(text: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def _run_rerank(query: str, parent_texts: Dict[str, str], parent_meta: Dict[str, Dict]) -> List[Tuple[str, float]]:
    """Rerank parents with cross-encoder. Returns (parent_block_id, score) sorted desc."""
    from rerank import _rerank as rerank_fn
    return rerank_fn(query, parent_texts, parent_meta)


def _retrieve(
    query: str,
    topk: int,
    vectors_path: str,
    rerank: bool = False,
    topn: int = 50,
) -> Tuple[List[Tuple[Dict, float]], Dict[str, Dict], Dict[str, List[str]], Dict[str, ChunkRecord]]:
    """Run retrieval and expansion. Streams vectors/linked/chunks to avoid OOM."""
    stage1_k = max(topk, topn) if rerank else topk

    qvec = _embed_query_bge(query)
    print("Streaming vectors (low-memory)...", flush=True)
    top_rows = _stream_vectors_topk(vectors_path, qvec, stage1_k)
    if not top_rows:
        print("No text vectors found.")
        raise SystemExit(1)

    parent_meta: Dict[str, Dict] = {}
    for cid, doc_id, pid, score in top_rows:
        if pid not in parent_meta or score > parent_meta[pid]["score"]:
            parent_meta[pid] = {"doc_id": doc_id, "score": score}

    parent_ids = set(parent_meta.keys())
    by_parent = _load_linked_by_parents(LINKED_CHUNKS_JSONL, parent_ids)
    needed_cids: Set[str] = set()
    for cids in by_parent.values():
        needed_cids.update(cids)
    for pid in by_parent:
        by_parent[pid].sort(key=lambda cid: (_chunk_index(cid), cid))

    chunk_records = _load_chunk_records_for_ids(CHUNKS_JSONL, needed_cids)
    n_text = sum(1 for cid in needed_cids if (chunk_records.get(cid) or {}).get("text"))
    if n_text == 0 and needed_cids:
        print(
            "Warning: No chunk text found for retrieved IDs. "
            "chunks.jsonl may be out of sync with linked_chunks/real_vectors. "
            "Re-run: python chunk.py && python link.py && python real_embed.py",
            flush=True,
        )

    if rerank and parent_ids:
        parent_texts = {
            pid: _parent_text_for_rerank(by_parent[pid], chunk_records) for pid in parent_ids
        }
        parent_texts = {pid: t for pid, t in parent_texts.items() if t}
        if parent_texts:
            print("Reranking with cross-encoder...", flush=True)
            scored_parents = _run_rerank(query, parent_texts, parent_meta)
            scored_parents = scored_parents[:topk]
            parent_meta = {pid: {"doc_id": parent_meta.get(pid, {}).get("doc_id", ""), "score": s} for pid, s in scored_parents}
            by_parent = {pid: by_parent[pid] for pid in parent_meta if pid in by_parent}
            top = []
            for pid, s in scored_parents:
                cids = by_parent.get(pid, [])
                cid = cids[0] if cids else pid
                meta = parent_meta.get(pid, {})
                top.append(({"chunk_id": cid, "doc_id": meta.get("doc_id", ""), "parent_block_id": pid}, s))
        else:
            top = [
                ({"chunk_id": cid, "doc_id": doc_id, "parent_block_id": pid}, score)
                for (cid, doc_id, pid, score) in top_rows[:topk]
            ]
    else:
        top = [
            ({"chunk_id": cid, "doc_id": doc_id, "parent_block_id": pid}, score)
            for (cid, doc_id, pid, score) in top_rows[:topk]
        ]

    return top, parent_meta, by_parent, chunk_records


def _build_context(
    parent_meta: Dict[str, Dict],
    by_parent: Dict[str, List[str]],
    chunk_records: Dict[str, ChunkRecord],
    papers_meta: Dict[str, Dict[str, str]],
    include_image_chunks: bool = True,
) -> str:
    # Order parents by best score descending
    ordered = sorted(parent_meta.items(), key=lambda kv: -kv[1]["score"])
    blocks: List[str] = []
    for pid, meta in ordered:
        doc_id = meta["doc_id"]
        p_meta = papers_meta.get(doc_id, {})
        title = (p_meta.get("title") or "").strip()
        cids = by_parent.get(pid, [])
        text = _format_parent_content_for_llm(
            cids, chunk_records, include_image_chunks=include_image_chunks
        )
        text = _truncate_tokens(text)
        if not text:
            continue
        if title:
            header = f"=== DOC {doc_id} / {title} / {pid} ==="
        else:
            header = f"=== DOC {doc_id} / {pid} ==="
        blocks.append(f"{header}\n{text}")
    return "\n\n".join(blocks)


def _guess_image_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "application/octet-stream")


def _file_to_vision_data_url(path: str, max_edge: int) -> str | None:
    """Read image from disk; optionally downscale long edge for token/cost. Returns data URL or None."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        return None
    if not raw:
        return None

    if max_edge > 0:
        try:
            from io import BytesIO

            from PIL import Image

            im = Image.open(BytesIO(raw))
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            elif im.mode != "RGB":
                im = im.convert("RGB")
            w, h = im.size
            long_edge = max(w, h)
            if long_edge > max_edge:
                scale = max_edge / float(long_edge)
                nw = max(1, int(w * scale))
                nh = max(1, int(h * scale))
                im = im.resize((nw, nh), Image.Resampling.LANCZOS)
            buf = BytesIO()
            im.save(buf, format="JPEG", quality=88, optimize=True)
            b64 = base64.standard_b64encode(buf.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{b64}"
        except Exception:
            pass

    mime = _guess_image_mime(path)
    if mime == "application/octet-stream":
        return None
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _collect_vision_images(
    parent_meta: Dict[str, Dict],
    by_parent: Dict[str, List[str]],
    chunk_records: Dict[str, ChunkRecord],
    max_images: int,
) -> List[Tuple[str, str]]:
    """(chunk_id, absolute_path) in retrieval score order; dedupe by resolved path."""
    ordered = sorted(parent_meta.items(), key=lambda kv: -kv[1]["score"])
    seen: Set[str] = set()
    out: List[Tuple[str, str]] = []
    for _pid, _meta in ordered:
        sib = _sibling_text_table_corpus(by_parent.get(_pid, []), chunk_records)
        for cid in by_parent.get(_pid, []):
            if len(out) >= max_images:
                return out
            rec = chunk_records.get(cid) or {}
            if (rec.get("modality") or "text") != "image":
                continue
            if not _image_worth_embedding_in_report(cid, rec, sib):
                continue
            ap = (rec.get("asset_path") or "").strip()
            if not ap:
                continue
            ap_use = _prefer_png_asset_path_if_exists(ap)
            abs_p = _abs_project_path(ap_use)
            if not os.path.isfile(abs_p):
                continue
            key = os.path.normcase(os.path.normpath(abs_p))
            if key in seen:
                continue
            seen.add(key)
            out.append((cid, abs_p))
    return out


def _sanitize_figure_paths_in_prose(text: str) -> str:
    """LLM이 옛날 맥락처럼 .jpx 등을 쓴 경우 답변/References에서 .png로 통일."""
    if not text:
        return text
    return re.sub(
        r"((?:data/)?raw/pmid_\d+/page_\d+_fig_\d+)\.(?:jpx|jp2|j2k)\b",
        r"\1.png",
        text,
        flags=re.IGNORECASE,
    )


_READINGS_LINE_RE = re.compile(r"^\s*#\s*readings\s*:\s*(.+?)\s*$", re.IGNORECASE)


def _find_section_header_line_index(lines: List[str], readings_idx: int) -> int | None:
    """Walk upward from a '# readings : N' line to the nearest section title (unindented header)."""
    j = readings_idx - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    while j >= 0:
        ln = lines[j]
        if not ln.strip():
            j -= 1
            continue
        if re.match(r"^\s{2,}\S", ln):
            j -= 1
            continue
        st = ln.strip()
        if st.endswith(":") and re.match(r"^[A-Za-z]", st):
            return j
        j -= 1
    return None


def _inject_readings_into_header_line(header_line: str, count: str) -> str:
    """Append ', n=<count> <specific label>' before the trailing colon (styles 2 + 3)."""
    raw = header_line.rstrip("\n")
    lead = raw[: len(raw) - len(raw.lstrip())]
    stripped = raw.strip()
    if not stripped.endswith(":"):
        return header_line
    inner = stripped[:-1].rstrip()
    if re.search(r",\s*n\s*=", inner, flags=re.IGNORECASE):
        return header_line
    u = inner.upper()
    if u.startswith("CREATININE"):
        label = "creatinine measurements in this window"
    elif u.startswith("URINE OUTPUT"):
        label = "urine-output entries"
    else:
        label = "measurements in this section"
    count_st = count.strip()
    return f"{lead}{inner}, n={count_st} {label}:"


def _rewrite_readings_lines_in_case_text(text: str) -> str:
    """Replace '# readings : N' with an explicit count on the section header; drop the old line."""
    if not text or "# readings" not in text.lower():
        return text
    lines = text.splitlines()
    hits: List[Tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        m = _READINGS_LINE_RE.match(line)
        if not m:
            continue
        hidx = _find_section_header_line_index(lines, i)
        if hidx is None:
            continue
        hits.append((i, hidx, m.group(1).strip()))

    if not hits:
        return text

    for readings_idx, header_idx, count in sorted(hits, key=lambda t: -t[0]):
        lines[header_idx] = _inject_readings_into_header_line(lines[header_idx], count)
        del lines[readings_idx]

    return "\n".join(lines)


def _fenced_plaintext_block(text: str) -> str:
    """Case narrative for Summary: fenced block reads cleaner in MD previews than line-by-line '> ' quotes."""
    body = text.replace("\r\n", "\n").rstrip("\n")
    fence = "```"
    if "```" in body:
        fence = "~~~"
    if not body:
        return f"{fence}\n{fence}"
    return f"{fence}\n{body}\n{fence}"


def _format_case_summary_markdown(patient_data: str, question: str) -> str:
    """Unified ## Summary block for saved case markdown."""
    pd = _rewrite_readings_lines_in_case_text((patient_data or "").strip())
    q = (question or "").strip()
    parts: List[str] = ["## Summary\n\n"]
    if not pd:
        parts.append(
            "_No separate patient narrative was supplied._ The clinical scenario is described in **Questions** above.\n\n"
        )
        return "".join(parts)
    if pd == q:
        parts.append(
            "**Patient / treatment context** — same text as the retrieval query in **Questions** (verbatim):\n\n"
        )
        parts.append(_fenced_plaintext_block(pd))
        parts.append("\n\n")
        return "".join(parts)
    parts.append(
        "**Patient / treatment context** — verbatim from the case file (used to build the retrieval query in **Questions**):\n\n"
    )
    parts.append(_fenced_plaintext_block(pd))
    parts.append("\n\n")
    return "".join(parts)


def _call_llm(
    question: str,
    context: str,
    vision_items: List[Tuple[str, str]] | None = None,
) -> str:
    if not openai_api_key:
        print("KONG_API_KEY is not set in the environment.")
        raise SystemExit(1)

    model = os.environ.get("LLM_MODEL", "gpt-4o")

    max_edge = max(0, int(os.environ.get("VISION_MAX_EDGE", "1536")))

    system_msg = (
        "You are a medical literature research assistant. Your role is to synthesize evidence "
        "from peer-reviewed scientific papers (PubMed, Nature, Lancet, JAMA, BMJ, NEJM) to answer "
        "clinical and research questions.\n\n"
        "Host document structure: Questions and a patient Summary are already provided outside your reply. "
        "Your reply is ONLY the literature-based answer body. Do not output top-level headings "
        "that match the host sections (do not use '#', '## Questions', '## Summary', or '## Answer'). "
        "You may use '###' subheadings inside your answer (e.g., treatment options, references).\n"
        "Do not repeat a long patient narrative; briefly bridge to evidence when needed.\n\n"
        "### Sourcing rules\n"
        "- Answer using ONLY the provided context. Do not add information from general knowledge.\n"
        "- Cite sources using the paper title and parent_block_id together inside square brackets, in the format: [Paper Title (parent_block_id)]. Example: [Intensive blood-pressure lowering and cardiovascular outcomes (pmid_31638686_p2)]. Every factual claim must have at least one such citation.\n"
        "- Multi-source synthesis: whenever ≥2 distinct retrieved sources support a claim (different parent_block_ids, or different papers), cite at least 2 of them. Do not rely on a single parent_block_id for an entire answer when the context offers alternatives. Single-source claims are acceptable only if the context genuinely has no corroborating source.\n"
        "- Always consider potential adverse effects, contraindications, and drug–drug interactions mentioned in the context.\n"
        "- If the context does not contain enough information to answer or to personalize recommendations to an individual patient, clearly state this limitation.\n"
        "- If the context does not contain enough information to answer, clearly state: "
        "\"The provided literature does not contain sufficient information to answer this question.\"\n"
        "- Do not give direct medical advice. Frame answers as evidence summaries; recommend consulting a healthcare provider for clinical decisions.\n\n"
        "### Patient-grounded reasoning (mandatory when patient context is provided)\n"
        "- Before listing treatments, extract the patient's key clinical parameters from the patient context: vital signs (e.g., MAP, SBP/DBP, HR, SpO2, RR, temperature), labs (e.g., Cr, BUN, Hgb, lactate, K, Na, pH, bicarbonate), urine output (UO in mL/kg/h or mL over a window), comorbidities, and current medications. Use ONLY values present in the patient context — never invent or round numbers.\n"
        "- Quote at least 3 specific numeric values verbatim from the patient context in your answer, preserving units (e.g., \"Cr 3.2 mg/dL\", \"MAP 58 mmHg\", \"UO 0.3 mL/kg/h over 6 h\", \"Hgb 8.1 g/dL\", \"lactate 4.2 mmol/L\"). If fewer than 3 such values exist in the patient context, quote every one that is available.\n"
        "- Every treatment recommendation must be tied to one or more of these quoted values. Generic statements (e.g., \"given the patient's kidney injury\") without a numeric anchor are not acceptable when the patient context provides measurable values.\n\n"
        "### Output structure\n"
        "- Open with one short paragraph framing the clinical problem against the evidence, explicitly anchoring the framing to 2–3 quoted patient values. Do not re-dump the full case narrative.\n"
        "- Provide exactly three treatment suggestions, labeled 1., 2., and 3., in order of preference (1 = most preferred).\n"
        "- For each treatment option use this inline sub-structure:\n"
        "    - **Why this patient:** 1–3 sentences connecting the option to specific quoted patient values (e.g., \"MAP 58 mmHg with UO 0.3 mL/kg/h suggests inadequate perfusion, favoring …\"). Cite the supporting literature source(s) here.\n"
        "    - **When to use / contraindications:** when the option is appropriate vs. when it should be avoided (adverse effects, interactions, comorbidities), with citations.\n"
        "    - **Supporting sources:** list ≥1 cited parent_block_id in the canonical bracket format.\n"
        "- Explicitly describe fallback logic: if option 1 is not feasible for this patient (grounded in a specific quoted value — e.g., renal impairment per Cr 3.2 mg/dL, anemia per Hgb 6.8 g/dL, intolerance), then consider option 2; if option 2 is also not feasible, option 3. Each fallback trigger must cite a patient value.\n"
        "- End with a '### References' section listing each cited source as a bullet: paper title and parent_block_id, and one short note on what it supported (e.g., first-line therapy, safety).\n\n"
        "### Formatting\n"
        "- Figure assets in this project are PNG paths. If you mention a figure filename or path, use `.png` only; do not write `.jpx`, `.jp2`, or `.j2k`."
    )
    if vision_items:
        system_msg += (
            "\n\nFigure images may be attached after the text. Use them as evidence for structure and "
            "values shown in the figure (axes, flowcharts, plots). OCR in the text context can be "
            "noisy; prefer the image when they disagree. Still cite with [Paper Title (parent_block_id)]."
        )

    vision_note = ""
    if vision_items:
        vision_note = (
            "\n\nThe following figure image(s) are attached below in order. Each block is labeled "
            "with its chunk_id (match to image lines in context). "
            "Ground visual claims in these images.\n"
        )

    user_text = (
        f"Question:\n{question}\n\n"
        f"Context (from retrieved medical literature):\n{context}"
        f"{vision_note}\n"
        f"Based only on the context above"
        f"{' and the attached images' if vision_items else ''}, "
        f"provide an evidence-based answer with citations. "
        f"Before writing treatments, scan the Question text for concrete patient measurements "
        f"(e.g., vitals, labs, UO) and quote at least 3 of them verbatim with units in your answer. "
        f"Each of the 3 treatment options must include a 'Why this patient:' line that references "
        f"one or more of these quoted values, and should cite ≥2 distinct parent_block_ids whenever "
        f"the context supports it. "
        f"Remember: output only the answer body for the 'Answer' section—no '## Questions' or '## Summary'."
    )

    if vision_items:
        user_content: List[Dict[str, Any]] = [{"type": "text", "text": user_text}]
        for cid, abs_path in vision_items:
            url = _file_to_vision_data_url(abs_path, max_edge)
            if not url:
                user_content.append(
                    {
                        "type": "text",
                        "text": f"*(chunk `{cid}`: could not load image from disk)*\n",
                    }
                )
                continue
            user_content.append({"type": "text", "text": f"--- Figure chunk `{cid}` ---"})
            user_content.append({"type": "image_url", "image_url": {"url": url}})
        user_payload: str | List[Dict[str, Any]] = user_content
    else:
        user_payload = user_text

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_payload},
        ],
    )

    return resp.choices[0].message.content or ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve context and generate an answer with an LLM.")
    parser.add_argument("question", nargs="*", help="User question")
    parser.add_argument("--topk", type=int, default=5, help="Final top-k parents (default: 5)")
    parser.add_argument("--rerank", action="store_true", help="Use cross-encoder reranker (stage1 topn -> rerank -> topk)")
    parser.add_argument("--topn", type=int, default=50, help="Stage1 candidates when --rerank (default: 50)")
    parser.add_argument(
        "--vectors",
        default=DEFAULT_VECTORS_JSONL,
        help=f"Path to vectors JSONL (default: {DEFAULT_VECTORS_JSONL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only run retrieval and print assembled context; do not call the LLM.",
    )
    parser.add_argument(
        "--vision",
        action="store_true",
        help="Attach figure images (PNG/JPEG/WebP/GIF on disk) to the LLM as image_url; model sees "
        "pixels, not embedding vectors. Cap: VISION_MAX_IMAGES (default 6). Resize: VISION_MAX_EDGE "
        "(default 1536 long edge, JPEG). Also set GENERATE_VISION=1 to enable without the flag.",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Strip all image chunks (both OCR text and pixels) from the LLM context. Useful to "
        "isolate text-only answer behavior. Implicitly disables --vision if both are passed.",
    )
    parser.add_argument(
        "--case-id",
        type=str,
        default="",
        help="If set, save full output to outputs/{case_id}.md (e.g., case01_dementia_pharm_treatment).",
    )
    parser.add_argument(
        "--patient-data",
        type=str,
        default="",
        help="Raw patient data for optimized retrieval query. When provided, LLM generates best-fit "
        "question for treatment/diagnosis considering all conditions.",
    )
    parser.add_argument(
        "--patient-data-file",
        type=str,
        default="",
        metavar="PATH",
        help="UTF-8 text file read as patient data (same as --patient-data). Mutually exclusive with "
        "--patient-data. If --case-id is omitted, defaults to the file basename without extension.",
    )
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    patient_data = (args.patient_data or "").strip()
    pdata_file = (args.patient_data_file or "").strip()

    if pdata_file and patient_data:
        print("Use only one of --patient-data and --patient-data-file.", file=sys.stderr)
        raise SystemExit(2)
    if pdata_file:
        if not os.path.isfile(pdata_file):
            print(f"Not a file: {pdata_file}", file=sys.stderr)
            raise SystemExit(2)
        with open(pdata_file, encoding="utf-8") as _pf:
            patient_data = _pf.read().strip()

    # 1-2: Optimized query generation for retrieval/treatment-diagnosis
    if patient_data:
        try:
            from query_generator import generate_retrieval_query_for_treatment

            question = generate_retrieval_query_for_treatment(patient_data)
            print(f"Generated retrieval question: {question}\n")
        except ImportError:
            print("query_generator not available; using patient-data as question.")
            question = patient_data

    if not question:
        print("Please provide a question, --patient-data, or --patient-data-file, e.g.:")
        print("  python generate.py \"hippocampal MRI dementia\" --topk 5")
        print("  python generate.py --patient-data \"65yo male, dementia, hypertension, on ACE inhibitor\"")
        print("  python generate.py --patient-data-file /path/to/CASE_01.txt")
        raise SystemExit(1)

    topk = max(1, args.topk)
    topn = max(topk, args.topn) if args.rerank else topk
    vectors_path = args.vectors
    if vectors_path == DEFAULT_VECTORS_JSONL and not os.path.isfile(REAL_VECTORS_JSONL) and os.path.isfile(VECTORS_JSONL):
        vectors_path = VECTORS_JSONL
        print(f"Using {VECTORS_JSONL} (real_vectors.jsonl not found)", flush=True)

    papers_meta = _load_papers_meta(PAPERS_JSONL)
    top, parent_meta, by_parent, chunk_records = _retrieve(
        question,
        topk,
        vectors_path,
        rerank=args.rerank,
        topn=topn,
    )

    out_dir = os.path.join(_here, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    case_id = (args.case_id or "").strip()
    if not case_id and pdata_file:
        case_id = os.path.splitext(os.path.basename(pdata_file))[0]
    if case_id:
        out_path = os.path.join(out_dir, f"{case_id}.md")
    else:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = os.path.join(out_dir, f"result_{ts}.md")

    # Print top hits
    print("Top hits:" + (" (reranked)" if args.rerank else ""))
    for row, score in top:
        cid = row["chunk_id"]
        doc_id = row["doc_id"]
        pid = row["parent_block_id"]
        print(f"  {cid}  score={score:.4f}  doc_id={doc_id}  parent_block_id={pid}")

    text_only = bool(args.text_only)
    include_image_chunks = not text_only
    context = _build_context(
        parent_meta, by_parent, chunk_records, papers_meta,
        include_image_chunks=include_image_chunks,
    )
    if not context:
        print("\nNo context could be assembled; aborting LLM call.")
        print("  → Ensure chunks.jsonl, linked_chunks.jsonl, and real_vectors.jsonl are from the same run.")
        print("  → Re-run: python chunk.py && python link.py && python real_embed.py")
        raise SystemExit(1)

    if text_only and (args.vision or os.environ.get("GENERATE_VISION", "").lower() in ("1", "true", "yes")):
        print("\n--text-only is set; ignoring --vision (pixels + OCR both disabled).", flush=True)
    use_vision = (
        not text_only
        and (bool(args.vision) or os.environ.get("GENERATE_VISION", "").lower() in ("1", "true", "yes"))
    )
    max_vision = max(0, int(os.environ.get("VISION_MAX_IMAGES", "6")))

    if args.dry_run:
        print("\nAssembled context:\n")
        print(context)
        if text_only:
            print("\n--text-only: image chunks stripped from context (no OCR, no pixels).")
        if use_vision and max_vision > 0:
            v_items = _collect_vision_images(parent_meta, by_parent, chunk_records, max_vision)
            print(f"\n--vision: would attach {len(v_items)} image(s) (max {max_vision}):")
            for cid, ap in v_items:
                print(f"  {cid}  {ap}")
        elif use_vision:
            print("\n--vision: VISION_MAX_IMAGES is 0; no images would be attached.")
        print("\nUsed sources (markdown preview; paths relative to output file):\n")
        for pid in sorted(parent_meta.keys()):
            doc_id = parent_meta[pid]["doc_id"]
            p_meta = papers_meta.get(doc_id, {})
            title = (p_meta.get("title") or "").strip()
            cids = by_parent.get(pid, [])
            print(_format_used_source_markdown(pid, doc_id, title, cids, chunk_records, out_path))
        print("\nUsed source ids:")
        for pid in sorted(parent_meta.keys()):
            print(f"- {pid}")
        raise SystemExit(0)

    vision_items: List[Tuple[str, str]] | None = None
    if use_vision and max_vision > 0:
        vision_items = _collect_vision_images(parent_meta, by_parent, chunk_records, max_vision)
        if vision_items:
            print(
                f"\nVision: attaching {len(vision_items)} figure(s) to LLM (VISION_MAX_EDGE="
                f"{os.environ.get('VISION_MAX_EDGE', '1536')}).",
                flush=True,
            )
        else:
            print("\nVision: no on-disk figure chunks in retrieved parents; LLM call is text-only.", flush=True)
            vision_items = None

    answer = _sanitize_figure_paths_in_prose(_call_llm(question, context, vision_items) or "")

    # 터미널 출력 + MD 파일 자동 저장 (Questions → Summary → Answer → Used Sources)
    lines: list[str] = []
    lines.append(f"## Questions\n\n{question}\n\n")
    lines.append("**Run configuration**\n\n")
    lines.append(
        f"- **Vectors:** `{vectors_path}` | topk={topk}, rerank={args.rerank}, topn={topn}\n"
    )
    if vision_items:
        lines.append(
            f"- **Vision:** {len(vision_items)} figure(s) as `image_url` (pixels), max={max_vision} | "
            f"VISION_MAX_EDGE={os.environ.get('VISION_MAX_EDGE', '1536')}\n"
        )
    if text_only:
        lines.append("- **Text-only context:** image chunks stripped (no OCR, no pixels)\n")

    lines.append("\n---\n\n")
    lines.append(_format_case_summary_markdown(patient_data, question))
    lines.append("---\n\n### Answer (generated by LLM based on literature)\n\n")
    lines.append(answer or "")
    lines.append("\n\n---\n\n## Used Sources (with context)\n\n")

    # Retrieval hits 표 + score 설명 (<sub>) — Used Sources 섹션 상단에 위치
    if top:
        lines.append(
            "### Retrieval hits" + (" (reranked)" if args.rerank else "") + "\n\n"
        )
        lines.append("| rank | score | chunk_id | doc_id | parent_block_id |\n")
        lines.append("|------|-------|----------|--------|-----------------|\n")
        for i, (row, score) in enumerate(top, start=1):
            cid = row.get("chunk_id", "")
            doc_id = row.get("doc_id", "")
            pid = row.get("parent_block_id", "")
            lines.append(f"| {i} | {score:.4f} | `{cid}` | `{doc_id}` | `{pid}` |\n")
        if args.rerank:
            score_note = (
                "**Score**: cross-encoder relevance from BGE `bge-reranker-base` "
                "(stage-2, not normalized, can be negative; higher = more relevant). "
                f"Stage-1 candidates were top-{topn} by BGE `bge-base-en-v1.5` cosine similarity."
            )
        else:
            score_note = (
                "**Score**: cosine similarity between query and chunk embedding "
                "(BGE `bge-base-en-v1.5`, L2-normalized → dot product). "
                "Range ≈ [-1, 1]; higher = more relevant. "
                "Rule of thumb for BGE: &gt;0.7 strong, 0.5–0.7 moderate, &lt;0.5 weak."
            )
        lines.append(f"\n<sub>{score_note}</sub>\n\n")

    print("\nAnswer:\n")
    print(answer)

    print("\nUsed sources (with context):")
    for pid in sorted(parent_meta.keys()):
        doc_id = parent_meta[pid]["doc_id"]
        p_meta = papers_meta.get(doc_id, {})
        title = (p_meta.get("title") or "").strip()
        cids = by_parent.get(pid, [])
        block = _format_used_source_markdown(pid, doc_id, title, cids, chunk_records, out_path)
        has_body = any(
            (chunk_records.get(cid) or {}).get("text") or (chunk_records.get(cid) or {}).get("asset_path")
            for cid in cids
        )
        if not has_body:
            lines.append(
                f"- **{pid}** (doc_id={doc_id}, title={title or 'N/A'}) [no text or image path]\n\n"
            )
            print(f"- {pid} (doc_id={doc_id}, title={title}) [no text or image path]")
            continue
        if not block:
            # All children got filtered (e.g. uncited low-OCR images); skip parent entirely.
            continue
        print(block)
        lines.append(block)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    print(f"\nSaved full output to {out_path}")


if __name__ == "__main__":
    main()
