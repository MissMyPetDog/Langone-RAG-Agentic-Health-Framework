"""
JSONL schemas for minimal multimodal RAG pipeline (V1).

Each JSONL file has one JSON object per line.
Defined as TypedDict for type checking and serialization.
Supports cross-modal linkage via parent_block_id and retrieval expansion.
"""

from typing import Literal, TypedDict

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired


# -----------------------------------------------------------------------------
# papers.jsonl
# -----------------------------------------------------------------------------


class PaperRecord(TypedDict):
    doc_id: str
    title: str
    source: str
    fetched_at: str


# -----------------------------------------------------------------------------
# assets.jsonl
# -----------------------------------------------------------------------------


class AssetRecord(TypedDict):
    id: str
    doc_id: str
    kind: str
    path: str


# -----------------------------------------------------------------------------
# blocks.jsonl
# -----------------------------------------------------------------------------


class BlockRecord(TypedDict):
    block_id: str
    doc_id: str
    modality: Literal["text", "table", "image"]
    page: NotRequired[int]
    ref_id: NotRequired[str]
    text: NotRequired[str]
    asset_path: NotRequired[str]
    caption: NotRequired[str]


# -----------------------------------------------------------------------------
# chunks.jsonl
# -----------------------------------------------------------------------------


class ChunkRecord(TypedDict):
    chunk_id: str
    doc_id: str
    block_id: str
    modality: Literal["text", "table", "image"]
    text: NotRequired[str]
    asset_path: NotRequired[str]
    page: NotRequired[int]


# -----------------------------------------------------------------------------
# linked_chunks.jsonl
# -----------------------------------------------------------------------------


class LinkedChunkRecord(TypedDict):
    chunk_id: str
    doc_id: str
    block_id: str
    parent_block_id: str
    modality: Literal["text", "table", "image"]
    page: NotRequired[int]
    ref_id: NotRequired[str]
