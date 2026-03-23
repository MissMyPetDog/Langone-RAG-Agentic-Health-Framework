"""
Two-stage text-only retrieval with local reranker.

Stage 1: BGE dense retrieval over chunk embeddings (real_vectors).
Stage 2: Cross-encoder reranker (e.g., BAAI/bge-reranker-base) over parent_block texts.

Usage:
  python rerank.py "hippocampal MRI dementia" --topk 5 --topn 50 --vectors data/real_vectors.jsonl
"""
from __future__ import annotations

import sys
import os as _os

# venv 우선, 시스템 site-packages 맨 뒤 (typing_extensions 등 충돌 방지)
_here = _os.path.dirname(_os.path.abspath(__file__))
_venv_site = _os.path.join(_here, ".venv", "lib", "python3.10", "site-packages")
_sys_site = _os.path.join(_os.path.sep, "gpfs", "share", "apps", "python")
if _os.path.isdir(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

import argparse
import json
import math
import os
import re
from typing import Dict, List, Tuple

LINKED_CHUNKS_JSONL = "data/linked_chunks.jsonl"
CHUNKS_JSONL = "data/chunks.jsonl"
DEFAULT_VECTORS_JSONL = "data/real_vectors.jsonl"

BGE_MODEL = "BAAI/bge-base-en-v1.5"
DEFAULT_RERANK_MODEL = "BAAI/bge-reranker-base"
DEFAULT_RERANK_BATCH_SIZE = 16

SNIPPET_CHARS = 300


def _ensure_rerank_deps() -> None:
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    try:
        import sentence_transformers  # noqa: F401
        import transformers  # noqa: F401
        import torch  # noqa: F401
    except ImportError:
        print("Missing dependencies for reranker. Please install inside your virtualenv:")
        print("  pip install -U sentence-transformers transformers torch")
        raise SystemExit(1)


def _embed_query_bge(query: str) -> List[float]:
    from sentence_transformers import SentenceTransformer

    model_name = os.environ.get("EMBED_MODEL", BGE_MODEL)
    model = SentenceTransformer(model_name)
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
            out[rec["chunk_id"]] = rec
    return out


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


def _stage1_retrieve(
    query: str,
    topn: int,
    vectors_path: str,
) -> Tuple[List[Tuple[Dict, float]], List[Dict]]:
    """Stage 1: dense retrieval over all chunk vectors."""
    rows = _load_vectors(vectors_path)
    if not rows:
        print("No vectors loaded.")
        raise SystemExit(1)

    qvec = _embed_query_bge(query)
    scored: List[Tuple[Dict, float]] = []
    for row in rows:
        score = _dot(qvec, row["vector"])
        scored.append((row, score))
    scored.sort(key=lambda x: -x[1])
    top = scored[:topn]
    return top, rows


def _expand_parents(
    top_rows: List[Tuple[Dict, float]],
    all_rows: List[Dict],
    chunk_texts: Dict[str, str],
) -> Tuple[Dict[str, Dict], Dict[str, List[str]], Dict[str, str]]:
    """
    From topN chunks, expand to parent_block documents.

    Returns:
      parent_meta: parent_block_id -> {doc_id, best_stage1_score}
      by_parent: parent_block_id -> ordered list of chunk_ids
      parent_texts: parent_block_id -> concatenated text
    """
    parent_meta: Dict[str, Dict] = {}
    for row, score in top_rows:
        pid = row["parent_block_id"]
        doc_id = row.get("doc_id") or ""
        if pid not in parent_meta or score > parent_meta[pid]["score"]:
            parent_meta[pid] = {"doc_id": doc_id, "score": score}

    parent_ids = set(parent_meta.keys())
    by_parent: Dict[str, List[str]] = {pid: [] for pid in parent_ids}
    for row in all_rows:
        pid = row["parent_block_id"]
        if pid in by_parent:
            by_parent[pid].append(row["chunk_id"])

    # Sort chunks within each parent and build concatenated text
    parent_texts: Dict[str, str] = {}
    for pid, cids in by_parent.items():
        cids.sort(key=lambda cid: (_chunk_index(cid), cid))
        by_parent[pid] = cids
        parts = [chunk_texts.get(cid, "") for cid in cids]
        text = "\n\n".join(p for p in parts if p).strip()
        parent_texts[pid] = text

    # Drop parents with empty text
    for pid in list(parent_texts.keys()):
        if not parent_texts[pid]:
            parent_texts.pop(pid)
            by_parent.pop(pid, None)
            parent_meta.pop(pid, None)

    return parent_meta, by_parent, parent_texts


def _rerank(
    query: str,
    parent_texts: Dict[str, str],
    parent_meta: Dict[str, Dict],
) -> List[Tuple[str, float]]:
    """Stage 2 reranking with local cross-encoder (BGE reranker)."""
    _ensure_rerank_deps()
    from sentence_transformers import CrossEncoder

    model_name = os.environ.get("RERANK_MODEL", DEFAULT_RERANK_MODEL)
    batch_size_env = os.environ.get("RERANK_BATCH_SIZE")
    try:
        batch_size = int(batch_size_env) if batch_size_env else DEFAULT_RERANK_BATCH_SIZE
    except ValueError:
        batch_size = DEFAULT_RERANK_BATCH_SIZE
    batch_size = max(1, batch_size)

    model = CrossEncoder(model_name)

    # In-memory cache: (query, parent_block_id) -> score
    cache: Dict[Tuple[str, str], float] = {}

    parent_ids = list(parent_texts.keys())
    pairs = []
    idx_map: List[Tuple[str, str]] = []  # (pid, text_key)

    for pid in parent_ids:
        key = (query, pid)
        if key in cache:
            continue
        text = parent_texts[pid]
        if not text:
            continue
        pairs.append((query, text))
        idx_map.append((pid, "text"))

    scores: List[float] = []
    if pairs:
        scores = model.predict(pairs, batch_size=batch_size).tolist()

    # Fill cache
    for (pid, _), score in zip(idx_map, scores):
        cache[(query, pid)] = float(score)

    # Build sorted list of (pid, score)
    scored_parents: List[Tuple[str, float]] = []
    for pid in parent_ids:
        key = (query, pid)
        if key in cache:
            scored_parents.append((pid, cache[key]))

    scored_parents.sort(key=lambda x: -x[1])
    return scored_parents


def _snippet(text: str, max_chars: int = SNIPPET_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def main() -> None:
    parser = argparse.ArgumentParser(description="Two-stage retrieval with local BGE reranker.")
    parser.add_argument("question", nargs="*", help="Query string")
    parser.add_argument("--topk", type=int, default=5, help="Final topK parents to show (default: 5)")
    parser.add_argument("--topn", type=int, default=50, help="Initial embedding candidates (default: 50)")
    parser.add_argument(
        "--vectors",
        default=DEFAULT_VECTORS_JSONL,
        help=f"Path to vectors JSONL (default: {DEFAULT_VECTORS_JSONL})",
    )
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        print("Please provide a query, e.g.:")
        print('  python rerank.py "hippocampal MRI dementia" --topk 5 --topn 50')
        raise SystemExit(1)

    topk = max(1, args.topk)
    topn = max(topk, args.topn)
    vectors_path = args.vectors

    linked = _load_linked(LINKED_CHUNKS_JSONL)  # currently not strictly needed, but available for metadata
    chunk_texts = _load_chunk_texts(CHUNKS_JSONL)

    # Stage 1: dense retrieval
    top_rows, all_rows = _stage1_retrieve(question, topn, vectors_path)

    # Parent expansion
    parent_meta, by_parent, parent_texts = _expand_parents(top_rows, all_rows, chunk_texts)
    if not parent_meta:
        print("No parent blocks with non-empty text found.")
        raise SystemExit(1)

    # Stage 2: rerank parents
    scored_parents = _rerank(question, parent_texts, parent_meta)
    if not scored_parents:
        print("Reranker produced no scores.")
        raise SystemExit(1)

    print("Final reranked parents:")
    for pid, score in scored_parents[:topk]:
        meta = parent_meta[pid]
        doc_id = meta.get("doc_id", "")
        text = parent_texts.get(pid, "")
        print(f"- parent_block_id={pid}  doc_id={doc_id}  rerank_score={score:.4f}")
        if text:
            print(f"  snippet: {_snippet(text)}")
        cids = by_parent.get(pid, [])
        if cids:
            print("  chunks:")
            for cid in cids:
                print(f"    - {cid}")
        print()


if __name__ == "__main__":
    main()

