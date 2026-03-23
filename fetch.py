"""
Fetch papers from PubMed API, write papers.jsonl and assets.jsonl.
환자 질병명(disease) 기반으로 Nature, Lancet, JAMA, BMJ, NEJM 등 의학저널에서
literature 검색.

풀텍스트 PDF 획득 순서 (NYU VPN 연결 권장):
1. PMC OA - PMCID 있는 논문 (무료, FTP)
2. Unpaywall - DOI로 OA PDF URL (무료)
3. NYU VPN 시 publisher URL도 접근 가능
4. 풀텍스트 없으면 저장 안 함
"""

import json
import os
import re
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
]
JOURNAL_FILTER = " OR ".join(MEDICAL_JOURNALS)


def _pubmed_fetch(disease: str, max_results: int = 10) -> list[dict]:
    """
    PubMed E-utilities로 질병명(disease) 기반 literature 검색.
    Nature, Lancet, JAMA, BMJ, NEJM 등 주요 의학저널만 필터링.
    """
    import xml.etree.ElementTree as ET

    # 질병명 정규화 (빈 값이면 dementia 기본값)
    disease = re.sub(r"\s+", " ", disease.strip().replace('"', " ")).strip() or "dementia"

    # 검색 쿼리: 질병명 + 저널 필터
    term = f"({disease}) AND ({JOURNAL_FILTER})"
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance",
        "tool": "rag-fetch",
        "email": "kk5739@nyu.edu",
    }
    qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{qs}"

    req = Request(url, headers={"User-Agent": "multimodal-rag-fetch/1.0"})
    with urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    idlist = data.get("esearchresult", {}).get("idlist", [])
    if not idlist:
        print("PubMed: no results")
        return []

    # efetch로 상세 정보(제목, 초록) 가져오기
    ids = ",".join(idlist)
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
    entries = []

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

        # DOI, PMCID 추출
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
    # PMID → PMCID 변환 (PMC에 있는 논문만)
    if entries:
        pmids = [e["pmid"] for e in entries]
        pmcid_map = _get_pmcid_map(pmids)
        for e in entries:
            e["pmcid"] = e.get("pmcid") or pmcid_map.get(e["pmid"])

    print(f"PubMed: {len(entries)} articles from Nature/Lancet/JAMA/BMJ/NEJM")
    return entries


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
) -> tuple[list[PaperRecord], list[AssetRecord]]:
    """
    환자 질병명(disease) 기반으로 PubMed에서 literature 검색.
    existing_doc_ids가 있으면 해당 doc_id는 건너뛰고 새 논문만 반환 (증분 업데이트).
    """
    if use_stub:
        return _build_stub()

    try:
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

        # 1) PMC OA - PMCID 있는 논문 (무료)
        pmcid = e.get("pmcid")
        if pmcid and not got_pdf:
            pdf_url = _get_pmc_pdf_url(pmcid)
            if pdf_url and _download(pdf_url, pdf_path):
                got_pdf = True

        # 2) Unpaywall - DOI로 OA PDF (무료). NYU VPN 연결 시 publisher URL 접근 가능
        if not got_pdf and e.get("doi"):
            pdf_url = _get_unpaywall_pdf_url(e["doi"])
            if pdf_url and _download(pdf_url, pdf_path):
                got_pdf = True

        # 풀텍스트 없으면 저장 안 함
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
        print("No full-text PDFs available. Try with NYU VPN connected.")
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
    parser.add_argument("disease", nargs="*", help="Disease name (e.g., dementia, Alzheimer)")
    parser.add_argument(
        "--patient-info",
        type=str,
        default="",
        help="Patient information for optimized PubMed search (e.g., '65yo male, dementia, hypertension'). "
        "When provided, LLM generates best-fit search queries.",
    )
    args = parser.parse_args()

    disease = " ".join(args.disease).strip() if args.disease else "dementia"
    patient_info = (args.patient_info or "").strip()

    # 1-1: Optimized query generation for literature search
    if patient_info:
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

    papers, assets = fetch(disease, use_stub=use_stub, existing_doc_ids=existing_doc_ids if incremental else None)

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