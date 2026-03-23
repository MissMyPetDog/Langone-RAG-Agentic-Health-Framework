"""
Real semantic embeddings for text chunks using BGE (sentence-transformers).

Inputs: data/chunks.jsonl, data/linked_chunks.jsonl (paths relative to this script's directory)
Output: data/real_vectors.jsonl
"""
from __future__ import annotations

import sys
import os as _os

# 프로젝트 .venv를 앞에 두고, rag_venv 경로만 제거.
# (구버전: 프로젝트 밖 site-packages 전부 제거 → regex/idna 등이 공용에만 있을 때 ImportError)
_here = _os.path.dirname(_os.path.abspath(__file__))
_vi = sys.version_info
_venv_site = _os.path.join(
    _here, ".venv", "lib", f"python{_vi.major}.{_vi.minor}", "site-packages"
)


def _strip_conflicting_venv_paths() -> None:
    """torch/torchvision이 rag_venv에서 섞여 로드되는 경우만 차단."""
    banned = ("rag_venv",)
    kept: list[str] = []
    for p in sys.path:
        if p == "":
            kept.append(p)
            continue
        norm = p.replace("\\", "/")
        if any(b in norm for b in banned):
            continue
        kept.append(p)
    sys.path[:] = kept


if _os.path.isdir(_venv_site):
    _strip_conflicting_venv_paths()
    if _venv_site not in sys.path:
        sys.path.insert(0, _venv_site)
    _sys_site = _os.path.join(_os.path.sep + "gpfs", "share", "apps", "python")
    sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

for _k, _v in (
    ("OMP_NUM_THREADS", "1"),
    ("MKL_NUM_THREADS", "1"),
    ("OPENBLAS_NUM_THREADS", "1"),
    ("NUMEXPR_NUM_THREADS", "1"),
):
    _os.environ.setdefault(_k, _v)

import gc
import json
import math
import os
import tempfile
from typing import Dict, List, Tuple

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[misc, assignment]

CHUNKS_JSONL = _os.path.join(_here, "data", "chunks.jsonl")
LINKED_CHUNKS_JSONL = _os.path.join(_here, "data", "linked_chunks.jsonl")
REAL_VECTORS_JSONL = _os.path.join(_here, "data", "real_vectors.jsonl")
DEFAULT_MODEL = "BAAI/bge-base-en-v1.5"
DEFAULT_BATCH_SIZE = 1
DEFAULT_ENCODE_WINDOW = 4
DEFAULT_MAX_PASSAGE_CHARS = 16000


def _l2_normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in vec))
    return [x / n for x in vec] if n > 0 else vec


def _truncate_passage(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars]


def _load_linked(path: str) -> Dict[str, Dict]:
    linked: Dict[str, Dict] = {}
    if not os.path.isfile(path):
        return linked
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            linked[rec["chunk_id"]] = {
                "doc_id": rec["doc_id"],
                "parent_block_id": rec["parent_block_id"],
                "modality": rec["modality"],
            }
    return linked


def _scan_embed_targets(
    chunks_path: str,
    linked: Dict[str, Dict],
    incremental: bool,
    existing_ids: set[str],
) -> Tuple[int, List[str]]:
    """임베딩할 chunk_id 순서만 보관 (전체 청크 본문을 RAM에 올리지 않음)."""
    skipped = 0
    ordered_ids: List[str] = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            if chunk.get("modality") != "text":
                skipped += 1
                continue
            text = (chunk.get("text") or "").strip()
            if not text:
                skipped += 1
                continue
            cid = chunk["chunk_id"]
            if cid not in linked:
                skipped += 1
                continue
            if incremental and cid in existing_ids:
                skipped += 1
                continue
            ordered_ids.append(cid)
    return skipped, ordered_ids


def _load_texts_for_chunk_ids(chunks_path: str, want: set[str]) -> Dict[str, str]:
    """chunks.jsonl 한 번 순회로 임베딩 대상 chunk_id → 본문만 적재."""
    out: Dict[str, str] = {}
    if not want:
        return out
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            cid = chunk.get("chunk_id")
            if cid not in want:
                continue
            if chunk.get("modality") != "text":
                continue
            t = (chunk.get("text") or "").strip()
            if t:
                out[cid] = t
    return out


def main() -> None:
    model_name = os.environ.get("EMBED_MODEL", DEFAULT_MODEL)
    try:
        batch_size = int(os.environ.get("BATCH_SIZE", str(DEFAULT_BATCH_SIZE)))
    except ValueError:
        batch_size = DEFAULT_BATCH_SIZE
    batch_size = max(1, batch_size)
    try:
        encode_window = int(os.environ.get("ENCODE_WINDOW", str(DEFAULT_ENCODE_WINDOW)))
    except ValueError:
        encode_window = DEFAULT_ENCODE_WINDOW
    encode_window = max(1, encode_window)
    try:
        max_passage_chars = int(
            os.environ.get("MAX_PASSAGE_CHARS", str(DEFAULT_MAX_PASSAGE_CHARS))
        )
    except ValueError:
        max_passage_chars = DEFAULT_MAX_PASSAGE_CHARS

    import torch

    device_env = os.environ.get("DEVICE", "").lower()
    if device_env:
        device = device_env if device_env in ("cuda", "cpu", "mps") else "cpu"
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
    if device == "cuda" and batch_size == 1:
        print(
            "Hint: GPU 사용 중입니다. 속도 향상을 위해 BATCH_SIZE=32 또는 64 시도 "
            "(예: BATCH_SIZE=32 .venv/bin/python real_embed.py)",
            flush=True,
        )

    print(
        f"Project root: {_here}\n"
        f"  chunks:  {CHUNKS_JSONL}\n"
        f"  linked: {LINKED_CHUNKS_JSONL}\n"
        f"  out:     {REAL_VECTORS_JSONL}",
        flush=True,
    )

    linked = _load_linked(LINKED_CHUNKS_JSONL)

    existing_vector_chunk_ids: set[str] = set()
    incremental = os.environ.get("INCREMENTAL", "").lower() in ("1", "true", "yes")
    if incremental and os.path.isfile(REAL_VECTORS_JSONL):
        with open(REAL_VECTORS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                existing_vector_chunk_ids.add(json.loads(line)["chunk_id"])
        if existing_vector_chunk_ids:
            print(
                f"Incremental: {len(existing_vector_chunk_ids)} existing vector id(s), "
                "embedding new text chunks only.",
                flush=True,
            )

    if not os.path.isfile(CHUNKS_JSONL):
        print(f"{CHUNKS_JSONL} not found.")
        raise SystemExit(1)

    skipped, ordered_chunk_ids = _scan_embed_targets(
        CHUNKS_JSONL, linked, incremental, existing_vector_chunk_ids
    )

    if not ordered_chunk_ids:
        print("No chunks to embed.")
        print(f"Skipped: {skipped}")
        print(f"Output: {REAL_VECTORS_JSONL}")
        return

    want_ids = set(ordered_chunk_ids)
    text_by_id = _load_texts_for_chunk_ids(CHUNKS_JSONL, want_ids)
    missing = [cid for cid in ordered_chunk_ids if cid not in text_by_id]
    if missing:
        print(
            f"Warning: {len(missing)} chunk_id(s) not found or empty in chunks.jsonl; skipping.",
            flush=True,
        )
        ordered_chunk_ids = [cid for cid in ordered_chunk_ids if cid in text_by_id]
        skipped += len(missing)
    if not ordered_chunk_ids:
        print("No chunk texts available after load.")
        raise SystemExit(1)

    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer

    print(f"Loading model '{model_name}' on device={device}...", flush=True)
    print(
        f"To embed: {len(ordered_chunk_ids)} chunk(s); window={encode_window}; "
        f"MAX_PASSAGE_CHARS={max_passage_chars}",
        flush=True,
    )
    model = SentenceTransformer(model_name, device=device)

    n_chunks = len(ordered_chunk_ids)
    n_win = (n_chunks + encode_window - 1) // encode_window
    win_iter = range(0, n_chunks, encode_window)
    if tqdm is not None:
        win_iter = tqdm(win_iter, total=n_win, desc="encode windows", unit="win")

    out_dir = _os.path.dirname(REAL_VECTORS_JSONL) or _here
    os.makedirs(out_dir, exist_ok=True)

    # 증분 + 기존 파일: 임시파일에 모았다가 끝에만 교체하면 중간 Killed 시 진행이 전부 사라짐.
    # → 기존 벡터는 그대로 두고 새 임베딩만 파일 끝에 append + 윈도마다 fsync (재실행 시 INCREMENTAL로 이어감).
    append_to_existing = incremental and os.path.isfile(REAL_VECTORS_JSONL)
    tmp_path: str | None = None
    out_fp = None

    try:
        if append_to_existing:
            need_nl = False
            with open(REAL_VECTORS_JSONL, "rb") as _rf:
                _rf.seek(0, _os.SEEK_END)
                _sz = _rf.tell()
                if _sz > 0:
                    _rf.seek(-1, _os.SEEK_END)
                    if _rf.read(1) != b"\n":
                        need_nl = True
            out_fp = open(REAL_VECTORS_JSONL, "a", encoding="utf-8")
            if need_nl:
                out_fp.write("\n")
            print(
                "Incremental append mode: each window is flushed to disk (safe to resume if killed).",
                flush=True,
            )
        else:
            fd, tmp_path = tempfile.mkstemp(
                suffix=".jsonl.tmp", prefix="real_vectors_", dir=out_dir, text=True
            )
            out_fp = os.fdopen(fd, "w", encoding="utf-8")

        for start in win_iter:
            id_slice = ordered_chunk_ids[start : start + encode_window]
            batch_ids: List[str] = []
            texts: List[str] = []
            for cid in id_slice:
                raw = text_by_id.get(cid)
                if not raw:
                    skipped += 1
                    continue
                batch_ids.append(cid)
                texts.append(
                    "passage: " + _truncate_passage(raw, max_passage_chars)
                )

            if not texts:
                continue

            with torch.inference_mode():
                part = model.encode(
                    texts,
                    normalize_embeddings=True,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )
            del texts
            gc.collect()

            for cid, row in zip(batch_ids, part):
                v = row.tolist() if hasattr(row, "tolist") else list(row)
                v = _l2_normalize(v)
                meta = linked[cid]
                rec = {
                    "chunk_id": cid,
                    "doc_id": meta["doc_id"],
                    "parent_block_id": meta["parent_block_id"],
                    "modality": meta["modality"],
                    "vector": v,
                }
                out_fp.write(json.dumps(rec, ensure_ascii=False) + "\n")

            for cid in batch_ids:
                text_by_id.pop(cid, None)
            del part
            gc.collect()

            out_fp.flush()
            try:
                os.fsync(out_fp.fileno())
            except OSError:
                pass

        out_fp.close()
        out_fp = None
        if tmp_path is not None:
            os.replace(tmp_path, REAL_VECTORS_JSONL)
            tmp_path = None
    finally:
        if out_fp is not None:
            try:
                out_fp.close()
            except OSError:
                pass
        if tmp_path and os.path.isfile(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    total_vecs = 0
    if os.path.isfile(REAL_VECTORS_JSONL):
        with open(REAL_VECTORS_JSONL, "r", encoding="utf-8") as f:
            total_vecs = sum(1 for line in f if line.strip())

    print(f"Embedded: {len(ordered_chunk_ids)} new chunk(s); lines in output: {total_vecs}")
    print(f"Skipped (non-embed): {skipped}")
    print(f"Output: {REAL_VECTORS_JSONL}")


if __name__ == "__main__":
    main()
