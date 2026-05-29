"""
Read data/chunks.jsonl (ChunkRecord), group by (doc_id, page), emit LinkedChunkRecord
with parent_block_id = {doc_id}_p{page}. Write data/linked_chunks.jsonl.
"""

import json
import os
from collections import defaultdict

from schema import LinkedChunkRecord

CHUNKS_PATH = "data/chunks.jsonl"
LINKED_PATH = "data/linked_chunks.jsonl"


def main() -> None:
    if not os.path.isfile(CHUNKS_PATH):
        print(f"Missing {CHUNKS_PATH}")
        return

    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            doc_id = chunk["doc_id"]
            page = chunk.get("page", 0)
            groups[(doc_id, page)].append(chunk)

    records: list[LinkedChunkRecord] = []
    for (doc_id, page), chunks in groups.items():
        parent_block_id = f"{doc_id}_p{page}"
        for c in chunks:
            rec: LinkedChunkRecord = {
                "chunk_id": c["chunk_id"],
                "doc_id": doc_id,
                "block_id": c["block_id"],
                "parent_block_id": parent_block_id,
                "modality": c["modality"],
            }
            if page != 0:
                rec["page"] = page
            if c["modality"] == "image":
                rec["ref_id"] = "Figure 1"
            elif c["modality"] == "table":
                rec["ref_id"] = "Table 1"
            records.append(rec)

    os.makedirs(os.path.dirname(LINKED_PATH), exist_ok=True)
    with open(LINKED_PATH, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} linked chunks -> {LINKED_PATH}")


if __name__ == "__main__":
    main()
