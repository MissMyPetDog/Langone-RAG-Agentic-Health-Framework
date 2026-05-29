"""Build papers.jsonl and assets.jsonl from PDFs currently in data/raw/.

For each doc_id (folder/pdf in data/raw/), extracts a title via:
  1. PDF /Title metadata (if non-empty and looks meaningful)
  2. fallback: largest font run on page 1 (concatenated text spans)

Also writes assets.jsonl (parse.py input) with one pdf row per doc_id.

Source label is inferred from the doc_id prefix:
  pmid_* -> pubmed
  nihms_* -> pubmed_central
  otherwise -> manual

Usage:
  module load python/gpu/3.10.6
  .venv/bin/python orchestrator_tools/build_papers_jsonl.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import fitz  # pymupdf

WORKSPACE = Path("/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739")
RAW_DIR = WORKSPACE / "data" / "raw"
OUT_PATH = WORKSPACE / "papers.jsonl"
ASSETS_PATH = WORKSPACE / "assets.jsonl"


def find_pdf(doc_id: str) -> Path | None:
    p1 = RAW_DIR / f"{doc_id}.pdf"
    p2 = RAW_DIR / doc_id / "fulltext.pdf"
    if p1.is_file():
        return p1
    if p2.is_file():
        return p2
    return None


JUNK_EXTENSIONS = (".indd", ".doc", ".docx", ".pdf", ".tex", ".pages")


def looks_meaningful(s: str) -> bool:
    if not s:
        return False
    t = s.strip()
    if len(t) < 8:
        return False
    tl = t.lower()
    bad = {"untitled", "microsoft word", "document", "untitled document"}
    if tl in bad or tl.startswith("untitled"):
        return False
    if any(tl.endswith(ext) for ext in JUNK_EXTENSIONS):
        return False
    if re.search(r"\b(microsoft word|adobe indesign)\b", tl):
        return False
    return True


def extract_title_from_first_page(pdf_path: Path, max_lines: int = 6) -> str:
    """Heuristic: pick the largest-font text run on page 1 (concatenating spans
    that share that size). Falls back to the first non-empty text line."""
    doc = fitz.open(str(pdf_path))
    try:
        if doc.page_count == 0:
            return ""
        page = doc.load_page(0)
        d = page.get_text("dict")
        spans = []
        for block in d.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    txt = (span.get("text") or "").strip()
                    if txt:
                        spans.append((float(span.get("size") or 0), txt, line, block))
        if not spans:
            return ""
        # group by font size descending; the largest run is usually the title
        max_size = max(s[0] for s in spans)
        title_parts = [t for sz, t, _, _ in spans if abs(sz - max_size) < 0.1]
        title = " ".join(title_parts).strip()
        # collapse whitespace
        title = re.sub(r"\s+", " ", title)
        # if title looks too short, fall back to first ~max_lines lines of plain text
        if len(title) < 12:
            plain = page.get_text("text").splitlines()
            for ln in plain[:max_lines]:
                if len(ln.strip()) >= 12:
                    title = ln.strip()
                    break
        return title
    finally:
        doc.close()


def extract_title(pdf_path: Path) -> tuple[str, str]:
    """Return (title, method) where method describes which source was used."""
    doc = fitz.open(str(pdf_path))
    try:
        meta_title = (doc.metadata.get("title") or "").strip()
    finally:
        doc.close()
    if looks_meaningful(meta_title):
        return meta_title, "pdf_metadata"
    extracted = extract_title_from_first_page(pdf_path)
    if extracted:
        return extracted, "first_page_largest_font"
    return "", "none"


def infer_source(doc_id: str) -> str:
    if doc_id.startswith("pmid_"):
        return "pubmed"
    if doc_id.startswith("nihms_"):
        return "pubmed_central"
    return "manual"


def main():
    doc_ids = set()
    for p in RAW_DIR.iterdir():
        if p.is_file() and p.suffix.lower() == ".pdf":
            doc_ids.add(p.stem)
        elif p.is_dir():
            doc_ids.add(p.name)
    doc_ids = sorted(doc_ids)

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    print(f"=== Building papers.jsonl from {RAW_DIR} ({len(doc_ids)} doc_ids) ===\n")

    paper_rows = []
    asset_rows = []
    for did in doc_ids:
        pdf = find_pdf(did)
        if pdf is None:
            print(f"  [SKIP] {did}: no pdf found")
            continue
        title, method = extract_title(pdf)
        source = infer_source(did)
        rel_pdf = str(pdf.relative_to(WORKSPACE))
        row = {
            "doc_id":     did,
            "title":      title,
            "source":     source,
            "pdf_path":   rel_pdf,
            "fetched_at": now,
        }
        paper_rows.append(row)
        asset_rows.append({
            "id": f"asset_{did}_pdf",
            "doc_id": did,
            "kind": "pdf",
            "path": rel_pdf,
        })
        print(f"  {did}")
        print(f"    title  ({method}): {title!r}")
        print(f"    source: {source}")
        print(f"    pdf   : {rel_pdf}")
        print()

    OUT_PATH.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in paper_rows))
    ASSETS_PATH.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in asset_rows))
    print(f"=== wrote {len(paper_rows)} entries to {OUT_PATH} ===")
    print(f"=== wrote {len(asset_rows)} entries to {ASSETS_PATH} ===")


if __name__ == "__main__":
    main()
