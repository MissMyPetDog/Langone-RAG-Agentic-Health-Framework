"""
V1 deterministic embedding: read chunks + linked_chunks, write vectors.jsonl.
Uses stdlib only (sha256); embedding_dim = 16.
"""

import hashlib
import json
import os

CHUNKS_JSONL = "data/chunks.jsonl"
LINKED_CHUNKS_JSONL = "data/linked_chunks.jsonl"
VECTORS_JSONL = "data/vectors.jsonl"
EMBEDDING_DIM = 16


def _input_string(chunk: dict) -> str:
    modality = chunk.get("modality", "text")
    if modality in ("text", "table"):
        return chunk.get("text") or ""
    if modality == "image":
        return chunk.get("asset_path") or chunk.get("chunk_id", "")
    return chunk.get("text") or ""


def _embed_string(s: str) -> list[float]:
    digest = hashlib.sha256(s.encode("utf-8")).digest()
    # 64 bytes for 16 floats (4 bytes each); repeat digest if needed
    raw = (digest + digest)[: 4 * EMBEDDING_DIM]
    vector = []
    for i in range(EMBEDDING_DIM):
        start = i * 4
        four = raw[start : start + 4]
        u = int.from_bytes(four, "big")
        vector.append(u / (2**32))
    return vector


def main() -> None:
    # Load linked_chunks: chunk_id -> {doc_id, parent_block_id, modality}
    linked: dict[str, dict] = {}
    if os.path.isfile(LINKED_CHUNKS_JSONL):
        with open(LINKED_CHUNKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                cid = rec["chunk_id"]
                linked[cid] = {
                    "doc_id": rec["doc_id"],
                    "parent_block_id": rec["parent_block_id"],
                    "modality": rec["modality"],
                }

    skipped = 0
    written = 0
    os.makedirs(os.path.dirname(VECTORS_JSONL) or ".", exist_ok=True)

    with open(VECTORS_JSONL, "w", encoding="utf-8") as out:
        with open(CHUNKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                chunk = json.loads(line)
                chunk_id = chunk["chunk_id"]
                if chunk_id not in linked:
                    skipped += 1
                    continue
                meta = linked[chunk_id]
                inp = _input_string(chunk)
                vector = _embed_string(inp)
                out.write(
                    json.dumps(
                        {
                            "chunk_id": chunk_id,
                            "doc_id": meta["doc_id"],
                            "parent_block_id": meta["parent_block_id"],
                            "modality": meta["modality"],
                            "vector": vector,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                written += 1

    if skipped:
        print(f"Warning: skipped {skipped} chunk(s) missing in linked map.")
    print(f"Wrote {written} vectors -> {VECTORS_JSONL}")


if __name__ == "__main__":
    main()
