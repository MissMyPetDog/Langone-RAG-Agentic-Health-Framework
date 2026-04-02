"""
Fetch papers from PubMed API, write papers.jsonl and assets.jsonl.
환자 질병명(disease) 기반으로 Nature, Lancet, JAMA, BMJ, NEJM, AJKD 등 의학저널에서
literature 검색.

풀텍스트 PDF 획득 순서 (NYU VPN 연결 권장):
1. PMC OA - PMCID 있는 논문 (무료, FTP)
2. Unpaywall - DOI로 OA PDF URL (무료)
3. NYU VPN 시 publisher URL도 접근 가능
4. 풀텍스트 없으면 저장 안 함

특정 1편: python fetch.py "doi-10...." 또는 --doi 10....
로컬 PDF: --local-pdf (DOI 1개, PMC/Unpaywall 실패 시 복사)
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.parse import quote_plus

from schema import AssetRecord, PaperRecord

# Optional: use requests only for download (larger files); stdlib for API
try:
    import requests
except ImportError:
    requests = None

PAPERS_JSONL = "papers.jsonl"
ASSETS_JSONL = "assets.jsonl"
RAW_DIR = "data/raw"

# Unpaywall API (이메일 필수, 하루 10만 건 무료)
UNPAYWALL_EMAIL = os.environ.get("UNPAYWALL_EMAIL", "kk5739@nyu.edu")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# -----------------------------------------------------------------------------
# Stub (deterministic, no API key)
# -----------------------------------------------------------------------------


def _stub_papers() -> list[PaperRecord]:
    t = _now_iso()
    return [
        {"doc_id": "doc1", "title": "Multimodal RAG for Scientific Documents", "source": "stub", "fetched_at": t},
        {"doc_id": "doc2", "title": "Cross-Modal Retrieval with Parent Block Expansion", "source": "stub", "fetched_at": t},
        {"doc_id": "doc3", "title": "Tables and Figures in PDF Parsing", "source": "stub", "fetched_at": t},
    ]


def _stub_assets() -> list[AssetRecord]:
    return [
        {"id": "asset_doc1_pdf", "doc_id": "doc1", "kind": "pdf", "path": "data/raw/doc1/paper.pdf"},
    ]


def _ensure_stub_raw_files(assets: list[AssetRecord]) -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    for a in assets:
        path = a["path"]
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        if not os.path.isfile(path):
            with open(path, "wb") as f:
                f.write(b"%PDF-1.4 stub\n")


def _build_stub() -> tuple[list[PaperRecord], list[AssetRecord]]:
    papers = []
    assets = []
    for p in _stub_papers():
        sanitized_doc_id = _sanitize_doc_id(p["doc_id"])
        paper = p.copy()
        paper["doc_id"] = sanitized_doc_id
        papers.append(paper)
    for a in _stub_assets():
        sanitized_doc_id = _sanitize_doc_id(a["doc_id"])
        asset = a.copy()
        asset["doc_id"] = sanitized_doc_id
        asset["id"] = f"asset_{sanitized_doc_id}_pdf"
        asset["path"] = f"data/raw/{sanitized_doc_id}/paper.pdf"
        assets.append(asset)
    _ensure_stub_raw_files(assets)
    return papers, assets


# -----------------------------------------------------------------------------
# PubMed API (NCBI E-utilities, no key required for <3 req/sec)
# Nature, Lancet, JAMA, BMJ, NEJM 등 주요 의학저널 지원
# -----------------------------------------------------------------------------

# PubMed API에서 검색할 의학 저널 (API 지원)
MEDICAL_JOURNALS = [
    '"Nature"[jour]',
    '"Lancet"[jour]',
    '"JAMA"[jour]',
    '"BMJ"[jour]',
    '"The New England Journal of Medicine"[jour]',
    '"American Journal of Kidney Diseases"[jour]',
]
JOURNAL_FILTER = " OR ".join(MEDICAL_JOURNALS)


def _dois_from_positional_cli(arg_joined: str) -> list[str] | None:
    s = (arg_joined or "").strip()
    if not s:
        return None
    m = re.match(r"(?i)^doi[-:]\s*(.+)$", s)
    if not m:
        return None
    rest = m.group(1).strip()
    return [rest] if rest else None


def _normalize_doi(s: str) -> str:
    s = (s or "").strip()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
    ):
        if s.lower().startswith(prefix.lower()):
            s = s[len(prefix) :].strip()
            break
    return s.strip()


def _pubmed_esearch_ids(term: str, max_results: int = 10, sort: str = "relevance") -> list[str]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": max_results,
        "sort": sort,
        "tool": "rag-fetch",
        "email": "kk5739@nyu.edu",
    }
    qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{qs}"
    req = Request(url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
    with urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return data.get("esearchresult", {}).get("idlist", [])


def _pubmed_efetch_article_dicts(pmids: list[str]) -> list[dict]:
    import xml.etree.ElementTree as ET

    if not pmids:
        return []
    ids = ",".join(pmids)
    fetch_params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml",
        "tool": "rag-fetch",
        "email": "kk5739@nyu.edu",
    }
    fetch_qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in fetch_params.items())
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{fetch_qs}"
    req = Request(fetch_url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
    with urlopen(req, timeout=30) as resp:
        xml_data = resp.read().decode()

    root = ET.fromstring(xml_data)
    entries: list[dict] = []

    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//PMID")
        pmid = (pmid_el.text or "").strip() if pmid_el is not None else None
        if not pmid:
            continue

        title_el = article.find(".//ArticleTitle")
        title = (title_el.text or "").strip().replace("\n", " ") if title_el is not None else ""

        abstract_parts = []
        for abst in article.findall(".//AbstractText"):
            if abst.text:
                abstract_parts.append(abst.text.strip())
            elif abst.attrib.get("Label"):
                abstract_parts.append(f"{abst.attrib['Label']}: (no text)")
        abstract = "\n\n".join(abstract_parts) if abstract_parts else ""

        doi = None
        pmcid = None
        for aid in article.findall(".//ArticleId"):
            id_type = aid.attrib.get("IdType", "")
            if id_type == "doi":
                doi = (aid.text or "").strip()
            elif id_type == "pmc":
                pmcid = (aid.text or "").strip()
        if not doi:
            eloc = article.find(".//ELocationID[@EIdType='doi']")
            if eloc is not None and eloc.text:
                doi = eloc.text.strip()

        source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        entries.append({
            "doc_id": f"pmid_{pmid}",
            "pmid": pmid,
            "title": title,
            "source": source_url,
            "abstract": abstract,
            "doi": doi,
            "pmcid": pmcid,
        })

    if entries:
        pmids_found = [e["pmid"] for e in entries]
        pmcid_map = _get_pmcid_map(pmids_found)
        for e in entries:
            e["pmcid"] = e.get("pmcid") or pmcid_map.get(e["pmid"])

    return entries


def _pubmed_fetch(disease: str, max_results: int = 10) -> list[dict]:
    disease = re.sub(r"\s+", " ", disease.strip().replace('"', " ")).strip() or "dementia"
    term = f"({disease}) AND ({JOURNAL_FILTER})"
    idlist = _pubmed_esearch_ids(term, max_results=max_results)
    if not idlist:
        print("PubMed: no results")
        return []
    entries = _pubmed_efetch_article_dicts(idlist)
    print(f"PubMed: {len(entries)} articles (journal filter)")
    return entries


def _pubmed_fetch_by_dois(dois: list[str]) -> list[dict]:
    all_entries: list[dict] = []
    seen_pmids: set[str] = set()
    for raw in dois:
        doi = _normalize_doi(raw)
        if not doi.startswith("10."):
            print(f"Skipping invalid DOI (expected 10....): {raw!r}")
            continue
        idlist = _pubmed_esearch_ids(f"{doi}[doi]", max_results=5)
        if not idlist:
            print(f"PubMed: no PMID for DOI {doi}")
            continue
        batch = _pubmed_efetch_article_dicts(idlist)
        for e in batch:
            if e["pmid"] in seen_pmids:
                continue
            seen_pmids.add(e["pmid"])
            all_entries.append(e)
    print(f"PubMed: {len(all_entries)} article(s) by DOI")
    return all_entries


def _get_pmcid_map(pmids: list[str]) -> dict[str, str]:
    """NCBI ID converter로 PMID → PMCID 매핑."""
    if not pmids:
        return {}
    ids = ",".join(pmids)
    params = {"ids": ids, "idtype": "pmid", "tool": "rag-fetch", "email": "kk5739@nyu.edu"}
    qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?{qs}"
    try:
        req = Request(url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
        with urlopen(req, timeout=15) as resp:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.read().decode())
        out = {}
        for rec in root.findall(".//record"):
            if rec.attrib.get("status") != "error":
                pmcid = rec.attrib.get("pmcid")
                pmid = rec.attrib.get("pmid")
                if pmcid and pmid:
                    out[pmid] = pmcid
        return out
    except Exception:
        return {}


def _get_pmc_pdf_url(pmcid: str) -> str | None:
    """PMC OA API로 PMCID에 해당하는 PDF URL 반환."""
    if not pmcid or not pmcid.upper().startswith("PMC"):
        return None
    params = {"id": pmcid, "tool": "rag-fetch", "email": "kk5739@nyu.edu"}
    qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?{qs}"
    try:
        req = Request(url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
        with urlopen(req, timeout=15) as resp:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.read().decode())
        for link in root.findall(".//link[@format='pdf']"):
            href = link.attrib.get("href")
            if href:
                return href
        return None
    except Exception:
        return None


def _get_unpaywall_pdf_url(doi: str) -> str | None:
    """Unpaywall API로 DOI에 해당하는 OA PDF URL 반환."""
    if not doi or not UNPAYWALL_EMAIL:
        return None
    doi_clean = doi.strip()
    if not doi_clean.startswith("10."):
        return None
    url = f"https://api.unpaywall.org/v2/{quote_plus(doi_clean)}?email={quote_plus(UNPAYWALL_EMAIL)}"
    try:
        req = Request(url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        loc = data.get("best_oa_location")
        if not loc:
            return None
        return loc.get("url_for_pdf") or loc.get("url")
    except Exception:
        return None


def _download(url: str, path: str) -> bool:
    """URL에서 파일 다운로드. FTP/HTTPS 지원. 성공 시 True."""
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if url.startswith("ftp://"):
            with urlopen(url, timeout=60) as resp:
                body = resp.read()
            with open(path, "wb") as f:
                f.write(body)
        elif requests and not url.startswith("ftp://"):
            r = requests.get(url, timeout=60, stream=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            req = Request(url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
            with urlopen(req, timeout=60) as resp:
                body = resp.read()
            with open(path, "wb") as f:
                f.write(body)
        return os.path.isfile(path) and os.path.getsize(path) > 0
    except Exception:
        return False


def _sanitize_doc_id(doc_id: str) -> str:
    return re.sub(r'[^A-Za-z0-9]', '_', doc_id)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def fetch(
    disease: str,
    use_stub: bool = False,
    existing_doc_ids: set[str] | None = None,
    dois: list[str] | None = None,
    local_pdf: str | None = None,
) -> tuple[list[PaperRecord], list[AssetRecord]]:
    if use_stub:
        return _build_stub()

    try:
        if dois:
            entries = _pubmed_fetch_by_dois(dois)
        else:
            entries = _pubmed_fetch(disease, max_results=10)
    except Exception as e:
        print("PubMed fetch failed:", repr(e))
        return _build_stub()

    if not entries:
        return _build_stub()

    if existing_doc_ids:
        entries = [e for e in entries if _sanitize_doc_id(e["doc_id"]) not in existing_doc_ids]
        if not entries:
            print("Incremental: no new papers to add.")
            return [], []

    t = _now_iso()
    papers: list[PaperRecord] = []
    assets: list[AssetRecord] = []

    pdf_count = 0
    for e in entries:
        sanitized_doc_id = _sanitize_doc_id(e["doc_id"])
        doc_id = sanitized_doc_id
        raw_dir = os.path.join(RAW_DIR, doc_id)
        pdf_path = os.path.join(raw_dir, "fulltext.pdf")
        got_pdf = False

        pmcid = e.get("pmcid")
        if pmcid and not got_pdf:
            pdf_url = _get_pmc_pdf_url(pmcid)
            if pdf_url and _download(pdf_url, pdf_path):
                got_pdf = True

        if not got_pdf and e.get("doi"):
            pdf_url = _get_unpaywall_pdf_url(e["doi"])
            if pdf_url and _download(pdf_url, pdf_path):
                got_pdf = True

        if (
            not got_pdf
            and local_pdf
            and len(entries) == 1
            and os.path.isfile(local_pdf)
        ):
            try:
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                shutil.copy2(local_pdf, pdf_path)
                got_pdf = os.path.isfile(pdf_path) and os.path.getsize(pdf_path) > 0
                if got_pdf:
                    print(f"Using local PDF (fallback) -> {pdf_path}")
            except OSError as ex:
                print(f"Could not copy local PDF: {ex}")

        if not got_pdf:
            continue

        pdf_count += 1
        papers.append({
            "doc_id": doc_id,
            "title": e["title"],
            "source": "pubmed",
            "fetched_at": t,
        })
        assets.append({
            "id": f"asset_{doc_id}_pdf",
            "doc_id": doc_id,
            "kind": "pdf",
            "path": pdf_path,
        })

    if pdf_count:
        print(f"Downloaded {pdf_count} full-text PDF(s). Use NYU VPN for best access.")
    elif entries:
        print(
            "풀텍스트 PDF 없음: PMC OA / Unpaywall에 공개 링크가 없습니다. "
            '--local-pdf 로 로컬 PDF 경로를 주세요. 예: python fetch.py "doi-10...." --local-pdf ~/file.pdf'
        )
    return papers, assets


def write_jsonl(path: str, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _load_jsonl(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Fetch papers from PubMed (patient/disease based)")
    parser.add_argument(
        "disease",
        nargs="*",
        help="Disease search, OR: doi-10.... / doi:10.... (same as --doi).",
    )
    parser.add_argument(
        "--doi",
        action="append",
        default=[],
        metavar="DOI_OR_URL",
        help="Fetch this DOI exactly (repeatable).",
    )
    parser.add_argument(
        "--local-pdf",
        type=str,
        default="",
        metavar="PATH",
        help="With exactly one DOI: copy this file if PMC/Unpaywall has no PDF.",
    )
    parser.add_argument(
        "--patient-info",
        type=str,
        default="",
        help="Patient information for optimized PubMed search (e.g., '65yo male, dementia, hypertension'). "
        "When provided, LLM generates best-fit search queries.",
    )
    args = parser.parse_args()

    joined_pos = " ".join(args.disease).strip() if args.disease else ""
    pos_dois = _dois_from_positional_cli(joined_pos)
    flag_dois = [d.strip() for d in (args.doi or []) if d.strip()]
    dois_raw = (pos_dois or []) + flag_dois
    seen_norm: set[str] = set()
    dois: list[str] = []
    for d in dois_raw:
        key = _normalize_doi(d)
        if key and key not in seen_norm:
            seen_norm.add(key)
            dois.append(d)

    if pos_dois:
        disease = "dementia"
    elif joined_pos:
        disease = joined_pos
    else:
        disease = "dementia"

    patient_info = (args.patient_info or "").strip()
    local_pdf = (args.local_pdf or "").strip() or None
    if local_pdf and len(dois) != 1:
        print("Error: --local-pdf requires exactly one DOI.")
        raise SystemExit(1)
    if local_pdf and not os.path.isfile(local_pdf):
        print(f"Error: --local-pdf file not found: {local_pdf}")
        raise SystemExit(1)

    if dois and (joined_pos or patient_info):
        if pos_dois:
            print("Note: positional doi-... mode; ignoring --patient-info for PubMed.")
        else:
            print("Note: --doi set; ignoring positional disease and --patient-info.")

    # 1-1: Optimized query generation for literature search
    if patient_info and not dois:
        try:
            from query_generator import generate_pubmed_search_queries

            queries = generate_pubmed_search_queries(patient_info, max_queries=3)
            if queries:
                disease = queries[0]
                print(f"Generated PubMed search query: {disease}")
                if len(queries) > 1:
                    print(f"  (alternatives: {queries[1:]})")
        except ImportError:
            print("query_generator not available; using patient-info as-is.")
            disease = patient_info

    use_stub = os.environ.get("USE_STUB", "").lower() in ("1", "true", "yes")
    incremental = os.environ.get("INCREMENTAL", "").lower() in ("1", "true", "yes")

    existing_doc_ids: set[str] = set()
    if incremental:
        for r in _load_jsonl(PAPERS_JSONL):
            existing_doc_ids.add(r.get("doc_id", ""))
        if existing_doc_ids:
            print(f"Incremental: {len(existing_doc_ids)} existing doc(s) will be kept.")

    papers, assets = fetch(
        disease,
        use_stub=use_stub,
        existing_doc_ids=existing_doc_ids if incremental else None,
        dois=dois if dois else None,
        local_pdf=local_pdf,
    )

    if incremental and existing_doc_ids:
        existing_papers = _load_jsonl(PAPERS_JSONL)
        existing_assets = _load_jsonl(ASSETS_JSONL)
        combined_papers = existing_papers + papers
        combined_assets = existing_assets + assets
        write_jsonl(PAPERS_JSONL, combined_papers)
        write_jsonl(ASSETS_JSONL, combined_assets)
        print(f"Appended {len(papers)} papers (total {len(combined_papers)}) -> {PAPERS_JSONL}")
        print(f"Appended {len(assets)} assets (total {len(combined_assets)}) -> {ASSETS_JSONL}")
    else:
        write_jsonl(PAPERS_JSONL, papers)
        write_jsonl(ASSETS_JSONL, assets)
        print(f"Wrote {len(papers)} papers -> {PAPERS_JSONL}")
        print(f"Wrote {len(assets)} assets -> {ASSETS_JSONL}")


if __name__ == "__main__":
    main()