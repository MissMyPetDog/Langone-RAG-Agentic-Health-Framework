"""Wrapper around the partner's `generate._call_llm` for literature-grounded
treatment generation. Reuses their carefully-tuned system prompt verbatim.

The partner's prompt expects:
  - patient context (with quoted numeric values) embedded in the question
  - literature context formatted as a sequence of '=== DOC <doc> / <title> / <pid> ===' blocks
"""
import os
import sys
from pathlib import Path

# 1. Make sure KONG_API_KEY is in env (partner's module reads it at import time)
SQL_AGENT_PARENT = Path("/gpfs/data/razavianlab/capstone/2025_agentic")
if str(SQL_AGENT_PARENT) not in sys.path:
    sys.path.insert(0, str(SQL_AGENT_PARENT))
from sql_agent.config import KONG_API_KEY
if KONG_API_KEY and not os.environ.get("KONG_API_KEY"):
    os.environ["KONG_API_KEY"] = KONG_API_KEY

# 2. Make partner's module importable
PARTNER_PATH = Path(os.environ.get(
    "LIT_RAG_PATH",
    "/gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739",
))
if str(PARTNER_PATH) not in sys.path:
    sys.path.insert(0, str(PARTNER_PATH))

# 3. Import partner's LLM call (their system prompt + Kong client setup baked in)
from generate import _call_llm as _partner_call_llm  # noqa: E402


def _format_literature_context(blocks, truncate_each=1500):
    """Format a list of {parent_block_id, doc_id, title, text} dicts as the partner's
    expected '=== DOC ... ===' context format.
    """
    parts = []
    seen = set()
    for b in blocks:
        pid = b.get("parent_block_id")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        doc_id = b.get("doc_id", "")
        title = (b.get("title") or "").strip()
        text = (b.get("text") or "").strip()
        if not text:
            continue
        if len(text) > truncate_each:
            text = text[:truncate_each].rstrip() + "..."
        if title:
            header = f"=== DOC {doc_id} / {title} / {pid} ==="
        else:
            header = f"=== DOC {doc_id} / {pid} ==="
        parts.append(f"{header}\n{text}")
    return "\n\n".join(parts)


def generate_recommendation(question, literature_blocks):
    """Call the partner's _call_llm to produce a literature-grounded recommendation.

    Args:
        question: full question string. Must contain patient context with quoted
                  numeric values (vitals, labs, meds), followed by the clinical question.
        literature_blocks: list of {parent_block_id, doc_id, title, text} dicts
                           accumulated from one or more retrieve_literature() calls.

    Returns:
        Markdown text answer (3 treatment options with citations + References section).
        See partner's system prompt for the exact output format.
    """
    context = _format_literature_context(literature_blocks)
    if not context:
        return "ERROR: no literature context to ground the recommendation on."
    return _partner_call_llm(question=question, context=context, vision_items=None)
