"""
In-memory vector search with parent_block_id expansion.
Reads data/vectors.jsonl; uses same deterministic embedding as embed.py.
"""

import argparse
import hashlib
import json
import math

VECTORS_JSONL = "data/vectors.jsonl"
CHUNKS_JSONL = "data/chunks.jsonl"
EMBEDDING_DIM = 16
DEFAULT_QUERY = "dementia multimodal"
SNIPPET_TOP = 220
SNIPPET_EXPANDED = 140
BGE_MODEL = "BAAI/bge-base-en-v1.5"


def _embed_string(s: str) -> list[float]:
    digest = hashlib.sha256(s.encode("utf-8")).digest()
    raw = (digest + digest)[: 4 * EMBEDDING_DIM]
    vector = []
    for i in range(EMBEDDING_DIM):
        start = i * 4
        four = raw[start : start + 4]
        u = int.from_bytes(four, "big")
        vector.append(u / (2**32))
    return vector


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _dot(a: list[float], b: list[float]) -> float:
    """Dot product (use when both vectors are L2-normalized -> cosine sim)."""
    return sum(x * y for x, y in zip(a, b))


def _embed_query_bge(query: str):
    import os
    from sentence_transformers import SentenceTransformer
    model_name = os.environ.get("EMBED_MODEL", BGE_MODEL)
    model = SentenceTransformer(model_name)
    query_text = "query: " + query
    vec = model.encode([query_text], normalize_embeddings=True)[0]
    # Ensure unit length
    n = math.sqrt(sum(x * x for x in vec))
    if n > 0:
        vec = [float(x) / n for x in vec]
    else:
        vec = vec.tolist() if hasattr(vec, "tolist") else list(vec)
    return vec


def _load_vectors(path: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _load_chunk_texts(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                cid = rec.get("chunk_id", "")
                raw = (rec.get("text") or "").strip().replace("\n", " ")
                out[cid] = raw
    except FileNotFoundError:
        pass
    return out


def _snippet(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."


def main() -> None:
    parser = argparse.ArgumentParser(description="Vector search with parent_block expansion")
    parser.add_argument("query", nargs="*", help="Search query (default: dementia multimodal)")
    parser.add_argument("--topk", type=int, default=3, help="Number of top results to take (default: 3)")
    parser.add_argument("--vectors", default="data/vectors.jsonl", help="Path to vectors JSONL (default: data/vectors.jsonl)")
    args = parser.parse_args()
    query = " ".join(args.query).strip() if args.query else DEFAULT_QUERY
    topk = max(1, args.topk)

    vectors_path = args.vectors
    print(f"Loading vectors from {vectors_path}")
    rows = _load_vectors(vectors_path)
    if not rows:
        print("No vectors loaded.")
        return

    chunk_texts = _load_chunk_texts(CHUNKS_JSONL)
    vec_dim = len(rows[0]["vector"]) if rows else 0
    if vec_dim == EMBEDDING_DIM:
        qvec = _embed_string(query)
        scored = [(row, _cosine_sim(qvec, row["vector"])) for row in rows]
    else:
        qvec = _embed_query_bge(query)
        scored = [(row, _dot(qvec, row["vector"])) for row in rows]
    scored.sort(key=lambda x: -x[1])
    top = scored[:topk]

    if top:
        scores = [s for _, s in top]
        print(f"Score (topk): min={min(scores):.4f} max={max(scores):.4f}")

    # Primary matches
    print("Top matches:")
    for row, score in top:
        print(f"  {row['chunk_id']}  score={score:.4f}  modality={row['modality']}  parent_block_id={row['parent_block_id']}")
        text = chunk_texts.get(row["chunk_id"], "")
        if text:
            print(f"    snippet: {_snippet(text, SNIPPET_TOP)}")

    parent_ids = {row["parent_block_id"] for row, _ in top}
    # All chunks that share any of these parent_block_ids, grouped by parent_block_id
    by_parent: dict[str, list[tuple[str, str]]] = {pid: [] for pid in parent_ids}
    for row in rows:
        pid = row["parent_block_id"]
        if pid in parent_ids:
            by_parent[pid].append((row["chunk_id"], row["modality"]))

    print("\nExpanded by parent_block_id:")
    for pid in sorted(by_parent):
        print(f"  {pid}:")
        for cid, mod in sorted(by_parent[pid]):
            print(f"    - {cid} ({mod})")
            text = chunk_texts.get(cid, "")
            if text:
                print(f"      snippet: {_snippet(text, SNIPPET_EXPANDED)}")


if __name__ == "__main__":
    main()
