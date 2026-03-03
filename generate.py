"""
End-to-end QA:
- Retrieve context from real_vectors (BGE) and chunks/linked_chunks
- Call an LLM via OpenAI Responses API to answer using ONLY that context.
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
import json
import math
import re
from typing import Dict, List, Tuple

from openai import OpenAI

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
) -> Tuple[List[Tuple[Dict, float]], Dict[str, Dict], Dict[str, List[str]], Dict[str, str]]:
    """Run retrieval and expansion. Text search first, then expand to include
    table/image chunks under same parent_block_id (multimodal은 text 매칭된 id에만).
    If rerank=True: stage1 topn -> cross-encoder rerank -> topk.
    """
    linked = _load_linked(LINKED_CHUNKS_JSONL)
    chunk_texts = _load_chunk_texts(CHUNKS_JSONL)
    all_by_parent = _linked_to_by_parent(linked)

    text_rows = _load_vectors(vectors_path)
    if not text_rows:
        print("No text vectors loaded.")
        raise SystemExit(1)

    qvec = _embed_query_bge(query)
    text_scored: List[Tuple[Dict, float]] = []
    for row in text_rows:
        score = _dot(qvec, row["vector"])
        text_scored.append((row, score))
    text_scored.sort(key=lambda x: -x[1])

    stage1_k = max(topk, topn) if rerank else topk
    top_rows = text_scored[:stage1_k]

    parent_meta: Dict[str, Dict] = {}
    for row, score in top_rows:
        pid = row["parent_block_id"]
        doc_id = row["doc_id"]
        if pid not in parent_meta or score > parent_meta[pid]["score"]:
            parent_meta[pid] = {"doc_id": doc_id, "score": score}

    parent_ids = set(parent_meta.keys())
    by_parent = {pid: list(all_by_parent.get(pid, [])) for pid in parent_ids}
    for pid in by_parent:
        by_parent[pid].sort(key=lambda cid: (_chunk_index(cid), cid))

    if rerank and parent_ids:
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

    return top, parent_meta, by_parent, chunk_texts


def _build_context(
    parent_meta: Dict[str, Dict],
    by_parent: Dict[str, List[str]],
    chunk_texts: Dict[str, str],
    papers_meta: Dict[str, Dict[str, str]],
) -> str:
    # Order parents by best score descending
    ordered = sorted(parent_meta.items(), key=lambda kv: -kv[1]["score"])
    blocks: List[str] = []
    for pid, meta in ordered:
        doc_id = meta["doc_id"]
        p_meta = papers_meta.get(doc_id, {})
        title = (p_meta.get("title") or "").strip()
        cids = by_parent.get(pid, [])
        parts = [chunk_texts.get(cid, "") for cid in cids]
        text = "\n\n".join(p for p in parts if p).strip()
        text = _truncate_tokens(text)
        if not text:
            continue
        if title:
            header = f"=== DOC {doc_id} / {title} / {pid} ==="
        else:
            header = f"=== DOC {doc_id} / {pid} ==="
        blocks.append(f"{header}\n{text}")
    return "\n\n".join(blocks)


def _call_llm(question: str, context: str) -> str:
    if not openai_api_key:
        print("KONG_API_KEY is not set in the environment.")
        raise SystemExit(1)

    model = os.environ.get("LLM_MODEL", "gpt-4o")

    system_msg = (
        "You are a medical literature research assistant. Your role is to synthesize evidence "
        "from peer-reviewed scientific papers (PubMed, Nature, Lancet, JAMA, BMJ, NEJM) to answer "
        "clinical and research questions.\n\n"
        "Rules:\n"
        "- Answer using ONLY the provided context. Do not add information from general knowledge.\n"
        "- Always consider potential adverse effects and drug–drug interactions mentioned in the context.\n"
        "- When patient-level data are provided (e.g., prior procedures, comorbidities, current and past medications), explicitly explain how these factors affect treatment choice and safety.\n"
        "- Cite sources using the paper title and parent_block_id together inside square brackets, in the format: [Paper Title (parent_block_id)]. For example: [Intensive blood-pressure lowering and cardiovascular outcomes (pmid_31638686_p2)]. Every factual claim should have at least one such citation.\n"
        "- Structure your answer like a short paper: briefly summarize the problem, then discuss evidence and trade-offs.\n"
        "- Provide exactly three treatment suggestions, labeled 1., 2., and 3., in order of preference (1 = most preferred).\n"
        "- For each treatment option, describe when it is appropriate, when it should be avoided (contraindications, adverse effects, interactions), and which cited sources support it.\n"
        "- Explicitly describe fallback logic: if option 1 is not feasible for this patient (e.g., renal impairment, prior intolerance, interactions), then consider option 2; if option 2 is also not feasible, then option 3, always grounding this reasoning in the provided context.\n"
        "- If the context does not contain enough information to answer or to personalize recommendations to an individual patient, clearly state this limitation.\n"
        "- If the context does not contain enough information to answer, clearly state: "
        "\"The provided literature does not contain sufficient information to answer this question.\"\n"
        "- Do not give direct medical advice. Frame answers as evidence summaries; recommend consulting a healthcare provider for clinical decisions.\n"
        "- Prefer structured responses: summarize findings, then present the three numbered treatment options with citations, and end with a brief 'References' section listing the cited parent_block_id values and their roles (e.g., first-line therapy evidence, safety/interaction data)."
    )
    user_msg = (
        f"Question:\n{question}\n\n"
        f"Context (from retrieved medical literature):\n{context}\n\n"
        f"Based only on the context above, provide an evidence-based answer with citations."
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
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
    args = parser.parse_args()
    question = " ".join(args.question).strip()
    if not question:
        print("Please provide a question, e.g.:")
        print("  python generate.py \"hippocampal MRI dementia\" --topk 5")
        raise SystemExit(1)

    topk = max(1, args.topk)
    topn = max(topk, args.topn) if args.rerank else topk
    vectors_path = args.vectors
    if vectors_path == DEFAULT_VECTORS_JSONL and not os.path.isfile(REAL_VECTORS_JSONL) and os.path.isfile(VECTORS_JSONL):
        vectors_path = VECTORS_JSONL
        print(f"Using {VECTORS_JSONL} (real_vectors.jsonl not found)", flush=True)

    papers_meta = _load_papers_meta(PAPERS_JSONL)
    top, parent_meta, by_parent, chunk_texts = _retrieve(
        question,
        topk,
        vectors_path,
        rerank=args.rerank,
        topn=topn,
    )

    # Print top hits
    print("Top hits:" + (" (reranked)" if args.rerank else ""))
    for row, score in top:
        cid = row["chunk_id"]
        doc_id = row["doc_id"]
        pid = row["parent_block_id"]
        print(f"  {cid}  score={score:.4f}  doc_id={doc_id}  parent_block_id={pid}")

    context = _build_context(parent_meta, by_parent, chunk_texts, papers_meta)
    if not context:
        print("\nNo context could be assembled; aborting LLM call.")
        raise SystemExit(1)

    if args.dry_run:
        print("\nAssembled context:\n")
        print(context)
        print("\nUsed sources:")
        for pid in sorted(parent_meta.keys()):
            print(f"- {pid}")
        raise SystemExit(0)

    answer = _call_llm(question, context)

    print("\nAnswer:\n")
    print(answer)

    # Print which sources were used, along with their (possibly truncated) original text
    print("\nUsed sources (with context):")
    for pid in sorted(parent_meta.keys()):
        doc_id = parent_meta[pid]["doc_id"]
        p_meta = papers_meta.get(doc_id, {})
        title = (p_meta.get("title") or "").strip()
        cids = by_parent.get(pid, [])
        parts = [chunk_texts.get(cid, "") for cid in cids if chunk_texts.get(cid, "")]
        if not parts:
            if title:
                print(f"- {pid} (doc_id={doc_id}, title={title}) [no text]")
            else:
                print(f"- {pid} (doc_id={doc_id}) [no text]")
            continue
        text = "\n\n".join(parts).strip()
        text = _truncate_tokens(text)
        if title:
            header = f"=== DOC {doc_id} / {title} / {pid} ==="
        else:
            header = f"=== DOC {doc_id} / {pid} ==="
        print(f"\n{header}\n{text}")


if __name__ == "__main__":
    main()
