"""
Optimized/best-fit top-k query generation component.

1-1: PubMed/literature search - patient info → optimized search queries for papers
1-2: Retrieval/treatment-diagnosis - patient data → optimized retrieval query considering all conditions
"""
from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

# Reuse same OpenAI client setup as generate.py
openai_api_key = os.getenv("KONG_API_KEY")
if openai_api_key:
    from openai import OpenAI

    _client = OpenAI(
        base_url="https://kong-api.prod1.nyumc.org/gpt-4o/v1.3.0",
        api_key=openai_api_key,
        default_headers={"api-key": openai_api_key},
    )
else:
    _client = None


def generate_pubmed_search_queries(patient_info: str, max_queries: int = 3) -> List[str]:
    """
    1-1: 환자 정보 기반으로 PubMed/문헌 검색에 적합한 최적화된 검색 쿼리 생성.

    patient_info: 환자 정보 (질병명, 증상, 과거력, 복용약 등)
    max_queries: 반환할 쿼리 개수 (기본 3개)

    Returns: PubMed 검색에 사용할 쿼리 리스트 (relevance 순)
    """
    if not _client or not openai_api_key:
        # API 없으면 원본 그대로 반환
        return [patient_info.strip()] if patient_info.strip() else []

    system_msg = (
        "You are a medical literature search expert. Given patient information "
        "(disease, symptoms, comorbidities, medications, demographics), generate "
        "optimized PubMed search queries to find the most relevant papers from "
        "top medical journals (Nature, Lancet, JAMA, BMJ, NEJM).\n\n"
        "Rules:\n"
        "- Output 1-3 concise search terms, one per line.\n"
        "- Use medical MeSH-style terms when helpful (e.g., 'dementia', 'Alzheimer disease', 'mild cognitive impairment').\n"
        "- Prioritize the primary condition and key treatment/diagnosis aspects.\n"
        "- Each query should be a short phrase (3-8 words) suitable for PubMed search.\n"
        "- Output ONLY the queries, one per line, no numbering or extra text."
    )
    user_msg = f"Patient information:\n{patient_info}\n\nGenerate optimized PubMed search queries:"

    try:
        resp = _client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        content = (resp.choices[0].message.content or "").strip()
        lines = [q.strip() for q in content.split("\n") if q.strip()]
        # Remove numbering like "1.", "2)"
        cleaned = []
        for q in lines[:max_queries]:
            q = q.lstrip("0123456789.)- ")
            if q:
                cleaned.append(q)
        return cleaned if cleaned else [patient_info.strip()]
    except Exception as e:
        print(f"Query generation failed: {e}. Using original input.")
        return [patient_info.strip()] if patient_info.strip() else []


def generate_retrieval_query_for_treatment(patient_data: str) -> str:
    """
    1-2: 환자 데이터 기반으로 치료/진단 추천을 위한 최적화된 retrieval 쿼리 생성.

    patient_data: 환자 데이터 (질병, 증상, 과거력, 복용약, contraindications 등)
    모든 조건을 고려한 retrieval에 적합한 질문을 생성.

    Returns: RAG retrieval에 사용할 최적화된 질문 문자열
    """
    if not _client or not openai_api_key:
        return patient_data.strip()

    system_msg = (
        "You are a clinical decision support expert. Given patient data "
        "(disease, symptoms, comorbidities, current/past medications, "
        "contraindications, renal/hepatic function, etc.), generate a single "
        "optimized question for evidence-based treatment/diagnosis retrieval.\n\n"
        "Rules:\n"
        "- The question should capture ALL relevant conditions that affect treatment choice.\n"
        "- Include: primary diagnosis, key comorbidities, drug interactions, contraindications.\n"
        "- Phrase it so that retrieved literature can inform personalized treatment options.\n"
        "- Output ONE concise question (1-3 sentences), suitable for semantic search.\n"
        "- Output ONLY the question, no preamble or numbering."
    )
    user_msg = f"Patient data:\n{patient_data}\n\nGenerate optimized retrieval question for treatment/diagnosis:"

    try:
        resp = _client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        content = (resp.choices[0].message.content or "").strip()
        return content if content else patient_data.strip()
    except Exception as e:
        print(f"Query generation failed: {e}. Using original input.")
        return patient_data.strip()


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(
        description="Kong(LLM)으로 검색/리트리벌용 쿼리 생성. KONG_API_KEY 필요."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("pubmed", help="1-1: PubMed용 쿼리 여러 개 (환자 정보)")
    p1.add_argument("text", nargs="+", help="환자 정보 문장")
    p1.add_argument("-n", "--max", type=int, default=3, help="최대 쿼리 개수")

    p2 = sub.add_parser("retrieval", help="1-2: RAG retrieval용 질문 하나 (치료/진단)")
    p2.add_argument("text", nargs="+", help="환자 데이터 문장")

    args = p.parse_args()
    blob = " ".join(args.text).strip()
    if not blob:
        raise SystemExit("내용이 비었습니다.")

    if args.cmd == "pubmed":
        qs = generate_pubmed_search_queries(blob, max_queries=args.max)
        for i, q in enumerate(qs, 1):
            print(f"{i}. {q}")
    else:
        q = generate_retrieval_query_for_treatment(blob)
        print(q)
