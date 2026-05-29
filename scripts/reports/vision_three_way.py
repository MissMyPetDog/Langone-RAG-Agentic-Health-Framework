"""3-way comparison: vision (pixels+OCR) vs ocrOnly (default) vs textOnly.

Reads outputs/CASE_NN.md (vision), outputs/CASE_NN_ocrOnly.md, and
outputs/CASE_NN_textOnly.md for the same case ids and prints a markdown
report fragment with per-case + aggregate metrics.

Metrics per answer (Answer section only):
- word_count
- distinct cited parents (from "Used Sources" pmid_*_pNN section headers)
- numeric_value_hits  (e.g. "3.5 mg/dL", "92 mmHg", "0.5 mL/kg/h")
- patient_signal_hits (Hgb, SpO2, UO, Cr, MAP, sepsis, shock, lactate, ...)
- figure_ref_hits     (Figure N, .png, flowchart, diagram, axes)
- why_patient_lines   ("Why this patient:" occurrences)

Pairwise metrics (per case):
- jaccard 5-gram between (V,O), (V,T), (O,T)
- top-5 retrieval parent intersection across the three runs
"""

from __future__ import annotations

import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "outputs"

CASES = ["02", "03", "05", "06", "07", "08", "10", "17"]
VARIANTS = {
    "vision": "{n}.md",        # pixels + OCR
    "ocrOnly": "{n}_ocrOnly.md",  # OCR only
    "textOnly": "{n}_textOnly.md",  # neither
}

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
WHY_RE = re.compile(r"^\s*-\s*Why this patient\s*:", re.M)
PARENT_RE = re.compile(r"pmid_\d+_p(\d+)")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _section(text: str, header: str) -> str:
    """Return the body of an H2/H3 section by header text (until next heading)."""
    pat = re.compile(rf"^#{1,3}\s*{re.escape(header)}.*?$", re.M)
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


def _retrieval_table_parents(text: str) -> list[str]:
    """Top-k parent ids from the Retrieval hits table."""
    sec = _used_sources(text)
    pids = []
    for line in sec.splitlines():
        if not line.startswith("|"):
            continue
        if "rank" in line.lower() or "---" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        # rank | score | chunk_id | doc_id | parent_block_id
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


def _metrics(answer: str) -> dict:
    return {
        "words": _word_count(answer),
        "cite": len(_cited_parents(answer)),
        "num": len(NUM_RE.findall(answer)),
        "signal": len(SIGNAL_RE.findall(answer)),
        "figure": len(FIGURE_RE.findall(answer)),
        "why": len(WHY_RE.findall(answer)),
    }


def _agg(rows: list[dict], key: str) -> tuple[float, float]:
    vals = [r[key] for r in rows]
    if not vals:
        return 0.0, 0.0
    mu = statistics.mean(vals)
    sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    return mu, sd


def main() -> None:
    rows_per_variant: dict[str, list[dict]] = {v: [] for v in VARIANTS}
    pair_jaccard = {"V_O": [], "V_T": [], "O_T": []}
    retrieval_overlap = []
    cite_table = []

    print("# 3-way per-case metrics\n")
    print("| CASE | variant | words | cite | num | signal | figure | why |")
    print("|------|---------|------:|-----:|----:|-------:|-------:|----:|")

    for n in CASES:
        texts = {}
        answers = {}
        topk_parents = {}
        for v, tmpl in VARIANTS.items():
            t = _read(OUT / tmpl.format(n=f"CASE_{n}"))
            texts[v] = t
            answers[v] = _answer(t)
            topk_parents[v] = set(_retrieval_table_parents(t)[:5])
            m = _metrics(answers[v])
            rows_per_variant[v].append(m)
            print(
                f"| {n} | {v} | {m['words']} | {m['cite']} | {m['num']} | "
                f"{m['signal']} | {m['figure']} | {m['why']} |"
            )

        # pairwise jaccard
        jVO = _jaccard(answers["vision"], answers["ocrOnly"])
        jVT = _jaccard(answers["vision"], answers["textOnly"])
        jOT = _jaccard(answers["ocrOnly"], answers["textOnly"])
        pair_jaccard["V_O"].append(jVO)
        pair_jaccard["V_T"].append(jVT)
        pair_jaccard["O_T"].append(jOT)

        common3 = topk_parents["vision"] & topk_parents["ocrOnly"] & topk_parents["textOnly"]
        retrieval_overlap.append(len(common3))

        cite_table.append({
            "case": n,
            "V_cite": _cited_parents(answers["vision"]),
            "O_cite": _cited_parents(answers["ocrOnly"]),
            "T_cite": _cited_parents(answers["textOnly"]),
        })

    print("\n# Aggregate (μ ± sd)\n")
    print("| metric | vision | ocrOnly | textOnly | Δ(V−T) | Δ(V−O) | Δ(O−T) |")
    print("|--------|--------|---------|----------|-------:|-------:|-------:|")
    for key, label in [
        ("words", "word_count"),
        ("cite", "distinct cited parents"),
        ("num", "numeric_value_hits"),
        ("signal", "patient_signal_hits"),
        ("figure", "figure_ref_hits"),
        ("why", "why_patient_lines"),
    ]:
        mV, sV = _agg(rows_per_variant["vision"], key)
        mO, sO = _agg(rows_per_variant["ocrOnly"], key)
        mT, sT = _agg(rows_per_variant["textOnly"], key)
        print(
            f"| {label} | {mV:.2f}±{sV:.2f} | {mO:.2f}±{sO:.2f} | {mT:.2f}±{sT:.2f} | "
            f"{mV - mT:+.2f} | {mV - mO:+.2f} | {mO - mT:+.2f} |"
        )

    print("\n# Pairwise 5-gram Jaccard (per case)\n")
    print("| CASE | V↔O | V↔T | O↔T |")
    print("|------|-----|-----|-----|")
    for i, n in enumerate(CASES):
        print(f"| {n} | {pair_jaccard['V_O'][i]:.3f} | {pair_jaccard['V_T'][i]:.3f} | {pair_jaccard['O_T'][i]:.3f} |")
    print(
        f"| **mean** | **{statistics.mean(pair_jaccard['V_O']):.3f}** | "
        f"**{statistics.mean(pair_jaccard['V_T']):.3f}** | "
        f"**{statistics.mean(pair_jaccard['O_T']):.3f}** |"
    )

    print("\n# Retrieval top-5 intersection across all 3 variants\n")
    print("| CASE | common parents (out of 5) |")
    print("|------|---------------------------|")
    for n, c in zip(CASES, retrieval_overlap):
        print(f"| {n} | {c} |")
    print(f"| mean | {statistics.mean(retrieval_overlap):.2f} |")


if __name__ == "__main__":
    main()
