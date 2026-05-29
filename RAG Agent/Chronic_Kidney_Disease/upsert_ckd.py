"""
Upsert CKD-8 chunks to Chroma vector DB with BGE-M3 embeddings.
Based on upsert_aki_500.py (1:1 logic), only paths/collection name changed.
"""
import json
import os
import sys
import time
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

# === Config ===
JSONL_PATH      = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/ckd_8_chunks.jsonl"
DB_PATH         = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/NotesDB/ckd_8_db"
COLLECTION_NAME = "ckd_8_notes_bge"
BATCH_SIZE      = 500
LOG_INTERVAL    = 1000


def upsert_jsonl_to_chroma():
    print("=" * 60)
    print("Upsert CKD-8 Cohort Notes to Vector DB")
    print("=" * 60)

    # 1. Chroma client
    if not os.path.exists(DB_PATH):
        print(f"[*] Creating new database at: {DB_PATH}")
        os.makedirs(DB_PATH, exist_ok=True)
    else:
        print(f"[*] Using existing database at: {DB_PATH}")

    client = chromadb.PersistentClient(path=DB_PATH)

    # 2. BGE-M3 embedding function on GPU
    print("Loading BGE-M3 onto GPU...")
    try:
        bge_m3_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-m3",
            device="cuda"
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # 3. Get or create collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=bge_m3_ef,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"Collection '{COLLECTION_NAME}' ready.")

    # 4. Read JSONL, batch upsert
    if not os.path.exists(JSONL_PATH):
        print(f"JSONL file not found: {JSONL_PATH}")
        sys.exit(1)

    print(f"Reading: {JSONL_PATH}")
    file_size_mb = os.path.getsize(JSONL_PATH) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")

    batch_ids, batch_docs, batch_meta = [], [], []
    total_processed = 0
    total_upserted = 0
    start_time = time.time()

    with open(JSONL_PATH, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Upserting", mininterval=30.0):
            try:
                data = json.loads(line)
                batch_ids.append(str(data['chunk_id']))
                batch_docs.append(data['chunk_text'])
                batch_meta.append({
                    'note_id':      str(data.get('note_id') or ''),
                    'subject_id':   str(data.get('subject_id') or ''),
                    'hadm_id':      str(data.get('hadm_id') or ''),
                    'note_type':    str(data.get('note_type') or ''),
                    'note_seq':     int(data.get('note_seq') or 0),
                    'charttime':    str(data.get('charttime') or ''),
                    'storetime':    str(data.get('storetime') or ''),
                    'section_name': str(data.get('section_name') or ''),
                })
                total_processed += 1

                if total_processed % LOG_INTERVAL == 0:
                    elapsed = (time.time() - start_time) / 60
                    now = datetime.now().strftime('%H:%M:%S')
                    print(f"[{now}] Processed {total_processed:,} lines | "
                          f"Elapsed {elapsed:.1f} min")

                if len(batch_ids) >= BATCH_SIZE:
                    collection.upsert(
                        ids=batch_ids,
                        documents=batch_docs,
                        metadatas=batch_meta,
                    )
                    total_upserted += len(batch_ids)
                    batch_ids, batch_docs, batch_meta = [], [], []

            except json.JSONDecodeError:
                print("Skipped invalid JSON line")
            except KeyError as e:
                print(f"Skipped line missing key: {e}")

        # Flush final batch
        if batch_ids:
            collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
            )
            total_upserted += len(batch_ids)

    print("=" * 60)
    print("Upsert Complete")
    print(f"Total processed:    {total_processed:,}")
    print(f"Total upserted:     {total_upserted:,}")
    print(f"Collection count:   {collection.count():,}")
    print(f"Total time:         {(time.time() - start_time) / 60:.1f} min")
    print("=" * 60)


if __name__ == "__main__":
    upsert_jsonl_to_chroma()