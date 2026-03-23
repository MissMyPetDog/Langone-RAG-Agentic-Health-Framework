"""
Retrieval + context assembly for a query. No LLM.
Loads real_vectors, embeds query with BGE, expands by parent_block_id, prints hits and context blocks.
"""
from __future__ import annotations

import sys
import os as _os

# venv site-packages 최우선 (시스템 typing_extensions가 TypeIs 없어서 충돌 방지)
_here = _os.path.dirname(_os.path.abspath(__file__))
_venv_site = _os.path.join(_here, ".venv", "lib", "python3.10", "site-packages")
if _os.path.isdir(_venv_site):
    if _venv_site not in sys.path:
        sys.path.insert(0, _venv_site)
    # 시스템 site-packages를 뒤로 보내서 venv 패키지가 먼저 로드되게 함
    _sys_site = _os.path.join(_os.path.sep + "gpfs", "share", "apps", "python")
    sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

import argparse
import json
import math
import os
import re

LINKED_CHUNKS_JSONL = "data/linked_chunks.jsonl"
CHUNKS_JSONL = "data/chunks.jsonl"
REAL_VECTORS_JSONL = "data/real_vectors.jsonl"
VECTORS_JSONL = "data/vectors.jsonl"
BGE_MODEL = "BAAI/bge-base-en-v1.5"
MAX_CONTEXT_TOKENS = 1500
CHARS_PER_TOKEN = 4  # rough heuristic for truncation


def _embed_query_bge(query: str) -> list[float]:
    import time
    # 오프라인 미설정 시 온라인 허용 (캐시 없을 때 BGE 다운로드)
    from sentence_transformers import SentenceTransformer
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


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _load_linked(path: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
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


def _linked_to_by_parent(linked: dict[str, dict]) -> dict[str, list[str]]:
    """parent_block_id -> [chunk_ids] for all chunks (text + table + image)."""
    by_parent: dict[str, list[str]] = {}
    for cid, meta in linked.items():
        pid = meta["parent_block_id"]
        if pid not in by_parent:
            by_parent[pid] = []
        by_parent[pid].append(cid)
    return by_parent


def _load_chunk_texts(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["chunk_id"]] = (rec.get("text") or "").strip()
    return out


def _load_vectors(path: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _chunk_index(chunk_id: str) -> int:
    """Extract _cN from chunk_id for ordering (e.g. 2302_05894v2_p1_c2 -> 2)."""
    m = re.search(r"_c(\d+)$", chunk_id)
    return int(m.group(1)) if m else 0


def _truncate_tokens(text: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def _run_rerank(query: str, parent_texts: dict[str, str], parent_meta: dict[str, dict]) -> list[tuple[str, float]]:
    """Rerank parents with cross-encoder. Returns (parent_block_id, score) sorted desc."""
    from rerank import _rerank as rerank_fn
    return rerank_fn(query, parent_texts, parent_meta)


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieval + context assembly (no LLM)")
    parser.add_argument("query", nargs="*", help="Query string")
    parser.add_argument("--topk", type=int, default=5, help="Final top-k parents (default: 5)")
    parser.add_argument("--rerank", action="store_true", help="Use cross-encoder reranker (stage1 topn -> rerank -> topk)")
    parser.add_argument("--topn", type=int, default=50, help="Stage1 candidates when --rerank (default: 50)")
    args = parser.parse_args()
    query = " ".join(args.query).strip()
    if not query:
        parser.error("Query required. Example: python retrieval.py \"dementia risk factors\"")
    topk = max(1, args.topk)
    topn = max(topk, args.topn) if args.rerank else topk

    linked = _load_linked(LINKED_CHUNKS_JSONL)
    chunk_texts = _load_chunk_texts(CHUNKS_JSONL)
    all_by_parent = _linked_to_by_parent(linked)

    vectors_path = REAL_VECTORS_JSONL if os.path.isfile(REAL_VECTORS_JSONL) else VECTORS_JSONL
    print(f"Loading vectors from {vectors_path}", flush=True)
    text_rows = _load_vectors(vectors_path)
    if not text_rows:
        print("No vectors loaded.")
        return

    qvec = _embed_query_bge(query)
    text_scored = [(row, _dot(qvec, row["vector"])) for row in text_rows]
    text_scored.sort(key=lambda x: -x[1])
    top_rows = text_scored[:topn]

    parent_meta: dict[str, dict] = {}
    for row, score in top_rows:
        pid = row["parent_block_id"]
        doc_id = row["doc_id"]
        if pid not in parent_meta or score > parent_meta[pid]["score"]:
            parent_meta[pid] = {"doc_id": doc_id, "score": score}

    parent_ids = set(parent_meta.keys())
    by_parent = {pid: list(all_by_parent.get(pid, [])) for pid in parent_ids}
    for pid in by_parent:
        by_parent[pid].sort(key=lambda cid: (_chunk_index(cid), cid))

    if args.rerank and parent_ids:
        parent_texts = {
            pid: "\n\n".join(p for p in [chunk_texts.get(cid, "") for cid in by_parent[pid]] if p).strip()
            for pid in parent_ids
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
            top = top_rows[:topk]
    else:
        top = top_rows[:topk]

    print("Top hits:" + (" (reranked)" if args.rerank else ""))
    for row, score in top:
        if not row:
            continue
        cid = row["chunk_id"]
        doc_id = row["doc_id"]
        pid = row["parent_block_id"]
        print(f"  {cid}  score={score:.4f}  doc_id={doc_id}  parent_block_id={pid}")


    # 2) Expanded context blocks (concatenate texts, truncate to max tokens)
    print("\nExpanded context blocks:")
    ordered_parents = sorted(parent_meta.items(), key=lambda kv: -kv[1]["score"])
    for pid, _ in ordered_parents:
        cids = by_parent[pid]
        parts = [chunk_texts.get(cid, "") for cid in cids]
        block_text = "\n\n".join(p for p in parts if p).strip()
        block_text = _truncate_tokens(block_text)
        print(f"  [{pid}]")
        print(block_text)
        print()


if __name__ == "__main__":
    main()
