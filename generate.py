"""
End-to-end QA:
- Retrieve context from real_vectors (BGE) and chunks/linked_chunks
- Call an LLM via OpenAI API to answer using ONLY that context.
- Saved MD Used Sources include table text and markdown images (Preview-friendly paths).
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
            if ap:
                parts.append(f"[image file: {ap}]")
    return "\n\n".join(parts).strip()


def _format_parent_content_for_llm(cids: List[str], chunk_records: Dict[str, ChunkRecord]) -> str:
    parts: List[str] = []
    for cid in cids:
        rec = chunk_records.get(cid)
        if not rec:
            continue
        mod = rec.get("modality") or "text"
        if mod == "image":
            ap = rec.get("asset_path") or ""
            if ap:
                parts.append(f"[Image chunk {cid}]\nasset_path: {ap}")
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


def _markdown_image_line(asset_path: str, out_md_path: str) -> str:
    abs_img = _abs_project_path(asset_path)
    if not os.path.isfile(abs_img):
        return f"*(image not found on disk: `{asset_path}`)*"
    out_dir = os.path.dirname(out_md_path)
    rel = os.path.relpath(abs_img, start=out_dir)
    rel = rel.replace(os.sep, "/")
    base = os.path.basename(asset_path)
    return f"![{base}]({rel})"


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
    for cid in cids:
        rec = chunk_records.get(cid)
        if not rec:
            continue
        mod = rec.get("modality") or "text"
        if mod == "image":
            ap = rec.get("asset_path") or ""
            blocks.append(f"**`{cid}`** *(image)*\n")
            if ap:
                blocks.append(_markdown_image_line(ap, out_md_path))
                blocks.append("")
            else:
                blocks.append("*(no asset_path)*\n")
        elif mod == "table":
            t = rec.get("text") or ""
            blocks.append(f"**`{cid}`** *(table)*\n")
            blocks.append("```\n" + (t if t else "[empty]") + "\n```\n")
        else:
            t = rec.get("text") or ""
            if t:
                blocks.append(f"**`{cid}`** *(text)*\n\n{t}\n")
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
) -> str:
    # Order parents by best score descending
    ordered = sorted(parent_meta.items(), key=lambda kv: -kv[1]["score"])
    blocks: List[str] = []
    for pid, meta in ordered:
        doc_id = meta["doc_id"]
        p_meta = papers_meta.get(doc_id, {})
        title = (p_meta.get("title") or "").strip()
        cids = by_parent.get(pid, [])
        text = _format_parent_content_for_llm(cids, chunk_records)
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
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    patient_data = (args.patient_data or "").strip()

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
        print("Please provide a question or --patient-data, e.g.:")
        print("  python generate.py \"hippocampal MRI dementia\" --topk 5")
        print("  python generate.py --patient-data \"65yo male, dementia, hypertension, on ACE inhibitor\"")
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

    context = _build_context(parent_meta, by_parent, chunk_records, papers_meta)
    if not context:
        print("\nNo context could be assembled; aborting LLM call.")
        print("  → Ensure chunks.jsonl, linked_chunks.jsonl, and real_vectors.jsonl are from the same run.")
        print("  → Re-run: python chunk.py && python link.py && python real_embed.py")
        raise SystemExit(1)

    if args.dry_run:
        print("\nAssembled context:\n")
        print(context)
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

    answer = _call_llm(question, context)

    # 터미널 출력 + MD 파일 자동 저장
    lines: list[str] = []
    lines.append(f"# Question\n\n{question}\n\n")
    lines.append(f"**Vectors:** `{vectors_path}` | topk={topk}, rerank={args.rerank}, topn={topn}\n\n")
    lines.append("---\n\n## Answer\n\n")
    lines.append(answer or "")
    lines.append("\n\n---\n\n## Used Sources (with context)\n\n")

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
        print(block)
        lines.append(block)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    print(f"\nSaved full output to {out_path}")


if __name__ == "__main__":
    main()
