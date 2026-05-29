"""Wrapper around the partner's literature retrieval (agentic_rag_kk5739/retrieval.py).

Caches BGE model + vectors at module level. Returns blocks with title metadata so
the partner's `_call_llm` citation format works ([Paper Title (parent_block_id)]).
"""
import os
import sys
import json
from pathlib import Path

PARTNER_PATH = Path(os.environ.get(
    "LIT_RAG_PATH",
    "/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739",
))
if str(PARTNER_PATH) not in sys.path:
    sys.path.insert(0, str(PARTNER_PATH))

_LINKED = None
_CHUNK_TEXTS = None
_BY_PARENT = None
_VECTORS = None
_BGE = None
_PAPERS_META = None  # doc_id -> {title, source}


def _load_papers_meta():
    path = PARTNER_PATH / "papers.jsonl"
    out = {}
    if not path.is_file():
        return out
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
            if doc_id:
                out[doc_id] = {
                    "title": (rec.get("title") or "").strip(),
                    "source": (rec.get("source") or "").strip(),
                }
    return out


def _ensure_loaded():
    global _LINKED, _CHUNK_TEXTS, _BY_PARENT, _VECTORS, _BGE, _PAPERS_META
    if _VECTORS is not None:
        return

    from retrieval import (
        _load_linked, _linked_to_by_parent, _load_chunk_texts, _load_vectors,
        LINKED_CHUNKS_JSONL, CHUNKS_JSONL, REAL_VECTORS_JSONL, VECTORS_JSONL,
    )

    old_cwd = os.getcwd()
    os.chdir(PARTNER_PATH)
    try:
        _LINKED = _load_linked(LINKED_CHUNKS_JSONL)
        _CHUNK_TEXTS = _load_chunk_texts(CHUNKS_JSONL)
        _BY_PARENT = _linked_to_by_parent(_LINKED)
        vectors_path = REAL_VECTORS_JSONL if os.path.isfile(REAL_VECTORS_JSONL) else VECTORS_JSONL
        _VECTORS = _load_vectors(vectors_path)
    finally:
        os.chdir(old_cwd)

    _PAPERS_META = _load_papers_meta()

    from sentence_transformers import SentenceTransformer
    model_name = os.environ.get("EMBED_MODEL", "BAAI/bge-base-en-v1.5")
    _BGE = SentenceTransformer(model_name)


def _embed(query):
    vec = _BGE.encode(["query: " + query], normalize_embeddings=True)[0]
    return [float(x) for x in vec]


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _chunk_index(cid):
    import re
    m = re.search(r"_c(\d+)$", cid)
    return int(m.group(1)) if m else 0


def retrieve_literature(query, topk=5, max_chars_per_block=1200):
    """Search literature corpus.
    Returns list of {parent_block_id, doc_id, title, score, text}."""
    _ensure_loaded()
    qvec = _embed(query)

    scored = sorted(
        ((row, _dot(qvec, row["vector"])) for row in _VECTORS),
        key=lambda x: -x[1],
    )

    parent_meta = {}
    for row, score in scored[: topk * 5]:
        pid = row["parent_block_id"]
        if pid not in parent_meta or score > parent_meta[pid]["score"]:
            parent_meta[pid] = {"doc_id": row["doc_id"], "score": float(score)}

    sorted_parents = sorted(parent_meta.items(), key=lambda kv: -kv[1]["score"])[:topk]

    out = []
    for pid, meta in sorted_parents:
        cids = sorted(_BY_PARENT.get(pid, []), key=_chunk_index)
        text = "\n\n".join(_CHUNK_TEXTS.get(cid, "") for cid in cids).strip()
        if len(text) > max_chars_per_block:
            text = text[:max_chars_per_block].rstrip() + "..."
        title = (_PAPERS_META.get(meta["doc_id"], {}) or {}).get("title", "")
        out.append({
            "parent_block_id": pid,
            "doc_id": meta["doc_id"],
            "title": title,
            "score": meta["score"],
            "text": text,
        })
    return out
