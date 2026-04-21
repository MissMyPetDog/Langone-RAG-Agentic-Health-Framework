"""2-way comparison: vision (pixels + OCR) vs textOnly (no image chunks).

Reads outputs/CASE_NN.md (vision baseline) and outputs/CASE_NN_textOnly.md
for the 8 cases that retrieved at least one image chunk parent. Prints a
markdown report fragment with per-case + aggregate metrics.

Figure-usage is measured in three complementary ways:
  - explicit_figure_hits : regex over {"Figure N", ".png", "flowchart", ...}
  - image_parent_cited   : # parents cited in answer that host >=1 image chunk
  - ocr_shingle_borrow   : # 5-grams in answer that also appear in the OCR
                            text of any image chunk attached to a retrieved
                            parent for that case (proxy for "answer reuses
                            OCR-extracted figure content")
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "outputs"
CHUNKS_PATH = ROOT / "data" / "chunks.jsonl"


def _load_image_chunks() -> tuple[dict[str, str], dict[str, set[str]]]:
    """Return (ocr_by_parent, image_parents) where
       ocr_by_parent[parent_id] = concatenated OCR text of all image chunks under that parent,
       image_parents = set of parent_ids that have at least one image chunk.
    """
    ocr_by_parent: dict[str, list[str]] = {}
    image_parents: set[str] = set()
    if not CHUNKS_PATH.exists():
        return {}, set()
    for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("modality") != "image":
            continue
        pid = rec.get("parent_block_id") or ""
        if not pid:
            # sometimes image chunks carry parent in chunk_id like pmid_XXX_pN_fig_M
            m = re.match(r"(pmid_\d+_p\d+)_fig", rec.get("chunk_id") or "")
            if m:
                pid = m.group(1)
        if not pid:
            continue
        image_parents.add(pid)
        text = (rec.get("text") or "").strip()
        if text:
            ocr_by_parent.setdefault(pid, []).append(text)
    return {k: " ".join(v) for k, v in ocr_by_parent.items()}, image_parents

CASES = ["02", "03", "05", "06", "07", "08", "10", "17"]

NUM_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg/dL|mmol/L|mEq/L|mmHg|bpm|/min|°C|mL/kg/h|mL/h|%|g/dL|U/L)\b",
    re.I,
)
SIGNAL_RE = re.compile(
    r"\b(?:Hgb|hemoglobin|SpO2|UO|urine output|Cr\b|creatinine|MAP|BUN|sepsis|shock|lactate|"
    r"diuretic|vasopressor|fluid|loop|furosemide|norepinephrine|dialysis|RRT|nephrotoxin)\b",
    re.I,
)
FIGURE_RE = re.compile(r"\b(?:Figure\s+\d+|\.png|flowchart|diagram|axes)\b", re.I)
WHY_RE = re.compile(r"\*?\*?Why this patient\*?\*?\s*:", re.I)
PARENT_RE = re.compile(r"pmid_\d+_p(\d+)")
IMG_PARENTS_HINT_RE = re.compile(r"^###.*pmid_\d+_p(\d+).*$", re.M)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _section(text: str, header: str) -> str:
    pat = re.compile(r"^#{1,3}\s*" + re.escape(header) + r".*?$", re.M)
    m = pat.search(text)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^#{1,3}\s+\S", text[start:], re.M)
    return text[start: start + nxt.start()] if nxt else text[start:]


def _answer(text: str) -> str:
    return _section(text, "Answer")


def _used_sources(text: str) -> str:
    return _section(text, "Used Sources")


def _retrieval_topk_parents(text: str) -> list[str]:
    sec = _section(text, "Retrieval hits")
    pids = []
    for line in sec.splitlines():
        if not line.startswith("|"):
            continue
        if "rank" in line.lower() or "---" in line:
            continue
        cols = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(cols) >= 5:
            pid = cols[4]
            if pid.startswith("pmid_"):
                pids.append(pid)
    return pids


def _cited_parents(answer: str) -> set[str]:
    return set(PARENT_RE.findall(answer))


def _word_count(s: str) -> int:
    return len(re.findall(r"\b\w+\b", s))


def _shingles(s: str, n: int = 5) -> set[tuple[str, ...]]:
    toks = re.findall(r"\w+", s.lower())
    return {tuple(toks[i: i + n]) for i in range(len(toks) - n + 1)} if len(toks) >= n else set()


def _jaccard(a: str, b: str) -> float:
    sa, sb = _shingles(a), _shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _has_image_section(text: str) -> bool:
    """Heuristic: vision file has an `image_url`/`figure` mention in Used Sources block."""
    sec = _used_sources(text)
    return bool(re.search(r"!\[\s*[Ff]igure\b|\.png\)", sec))


def _metrics(answer: str, retrieved_parents: set[str],
             ocr_by_parent: dict[str, str], image_parents: set[str]) -> dict:
    cited = _cited_parents(answer)
    cited_full = {f"pmid_23499048_p{n}" for n in cited}
    image_parent_cited = len(cited_full & image_parents)

    # OCR shingle borrow: 5-gram overlap between answer and combined OCR text
    # of image chunks under THIS case's retrieved parents.
    ans_shingles = _shingles(answer)
    ocr_blob_parts = [ocr_by_parent[p] for p in (retrieved_parents & set(ocr_by_parent))]
    ocr_shingles = _shingles(" ".join(ocr_blob_parts)) if ocr_blob_parts else set()
    ocr_borrow = len(ans_shingles & ocr_shingles)

    return {
        "words": _word_count(answer),
        "cite": len(cited),
        "num": len(NUM_RE.findall(answer)),
        "signal": len(SIGNAL_RE.findall(answer)),
        "figure": len(FIGURE_RE.findall(answer)),
        "why": len(WHY_RE.findall(answer)),
        "img_parent_cite": image_parent_cited,
        "ocr_borrow": ocr_borrow,
    }


def _agg(rows: list[dict], key: str) -> tuple[float, float]:
    vals = [r[key] for r in rows]
    if not vals:
        return 0.0, 0.0
    mu = statistics.mean(vals)
    sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    return mu, sd


def main() -> None:
    ocr_by_parent, image_parents = _load_image_chunks()
    rows_v: list[dict] = []
    rows_t: list[dict] = []
    pair_jacc: list[float] = []
    overlap_topk: list[int] = []
    per_case = []

    for n in CASES:
        v_text = _read(OUT / f"CASE_{n}.md")
        t_text = _read(OUT / f"CASE_{n}_textOnly.md")
        v_ans = _answer(v_text)
        t_ans = _answer(t_text)
        v_top = set(_retrieval_topk_parents(v_text)[:5])
        t_top = set(_retrieval_topk_parents(t_text)[:5])
        v_m = _metrics(v_ans, v_top, ocr_by_parent, image_parents)
        t_m = _metrics(t_ans, t_top, ocr_by_parent, image_parents)
        rows_v.append(v_m)
        rows_t.append(t_m)
        j = _jaccard(v_ans, t_ans)
        pair_jacc.append(j)
        ov = len(v_top & t_top)
        overlap_topk.append(ov)
        per_case.append({
            "case": n,
            "v": v_m,
            "t": t_m,
            "jacc": j,
            "topk_common": ov,
            "v_top5": sorted(v_top),
            "t_top5": sorted(t_top),
        })

    print("# 2-way per-case metrics (Text-only vs Vision)\n")
    print("| CASE | variant | words | cite | num | sig | figExp | imgPCite | ocrBorrow | why |")
    print("|------|---------|------:|-----:|----:|----:|------:|---------:|----------:|----:|")
    for pc in per_case:
        n = pc["case"]
        for label, m in [("textOnly", pc["t"]), ("vision", pc["v"])]:
            print(
                f"| {n} | {label} | {m['words']} | {m['cite']} | {m['num']} | "
                f"{m['signal']} | {m['figure']} | {m['img_parent_cite']} | "
                f"{m['ocr_borrow']} | {m['why']} |"
            )

    print("\n# Aggregate (μ ± sd, paired N=8)\n")
    print("| metric | textOnly | vision | Δ(V−T) |")
    print("|--------|----------|--------|-------:|")
    for key, label in [
        ("words", "word_count"),
        ("cite", "distinct cited parents"),
        ("num", "numeric_value_hits"),
        ("signal", "patient_signal_hits"),
        ("figure", "figure_ref_explicit"),
        ("img_parent_cite", "image_parent_cited"),
        ("ocr_borrow", "ocr_shingle_borrow (5-gram)"),
        ("why", "why_patient_lines"),
    ]:
        mV, sV = _agg(rows_v, key)
        mT, sT = _agg(rows_t, key)
        print(f"| {label} | {mT:.2f}±{sT:.2f} | {mV:.2f}±{sV:.2f} | {mV - mT:+.2f} |")

    print("\n# Pairwise Jaccard (5-gram) and top-5 retrieval overlap\n")
    print("| CASE | answer Jaccard | top-5 common parents |")
    print("|------|---------------:|---------------------:|")
    for pc in per_case:
        print(f"| {pc['case']} | {pc['jacc']:.3f} | {pc['topk_common']} |")
    print(
        f"| **mean** | **{statistics.mean(pair_jacc):.3f}** | "
        f"**{statistics.mean(overlap_topk):.2f}** |"
    )

    print("\n# Direction agreement (per-case sign of Δ = textOnly − vision)\n")
    keys = [("words", "word_count"), ("cite", "cite"), ("signal", "patient_signal"),
            ("num", "numeric"), ("figure", "figure_ref_explicit"),
            ("img_parent_cite", "image_parent_cited"),
            ("ocr_borrow", "ocr_shingle_borrow")]
    print("| metric | T>V | T=V | T<V |")
    print("|--------|----:|----:|----:|")
    for k, label in keys:
        gt = sum(1 for pc in per_case if pc["t"][k] > pc["v"][k])
        eq = sum(1 for pc in per_case if pc["t"][k] == pc["v"][k])
        lt = sum(1 for pc in per_case if pc["t"][k] < pc["v"][k])
        print(f"| {label} | {gt} | {eq} | {lt} |")


if __name__ == "__main__":
    main()
