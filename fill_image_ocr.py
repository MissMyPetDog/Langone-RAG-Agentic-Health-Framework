#!/usr/bin/env python3
"""
이미지 블록의 빈 text 필드만 RapidOCR로 채움 (parse.py와 프로세스 분리 → OOM 완화).
전체 blocks를 먼저 메모리에 올린 뒤 갱신·저장하므로 중단 시에도 파일이 잘리지 않음.

사용:
  OCR_MAX_CHARS=4000 .venv/bin/python fill_image_ocr.py pmid_23499048
"""
from __future__ import annotations

import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
BLOCKS_JSONL = os.path.join(_here, "data", "blocks.jsonl")
OCR_MAX_CHARS = int(os.environ.get("OCR_MAX_CHARS", "4000"))


def _normalize_whitespace(text: str) -> str:
    lines = text.splitlines()
    out_lines: list[str] = []
    buf: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buf:
                out_lines.append(" ".join(buf))
                buf = []
            out_lines.append("")
        else:
            buf.append(stripped)
    if buf:
        out_lines.append(" ".join(buf))
    return "\n\n".join(line for line in out_lines if line != "" or (line == "" and out_lines))


def _write_blocks(path: str, rows: list[dict]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in rows:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: fill_image_ocr.py <doc_id> [doc_id ...]", file=sys.stderr)
        raise SystemExit(1)
    targets = frozenset(sys.argv[1:])
    from rapidocr_onnxruntime import RapidOCR

    eng = RapidOCR()
    if not os.path.isfile(BLOCKS_JSONL):
        print(f"Missing {BLOCKS_JSONL}", file=sys.stderr)
        raise SystemExit(1)

    rows: list[dict] = []
    with open(BLOCKS_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    n_fill = 0
    for i, rec in enumerate(rows):
        doc_id = rec.get("doc_id")
        if doc_id not in targets or rec.get("modality") != "image":
            continue
        # 이미 OCR 시도함(빈 문자열 포함)이면 스킵 — 무한 재시도 방지
        if rec.get("_ocr_attempted") or (rec.get("text") or "").strip():
            continue
        rel = rec.get("asset_path") or ""
        abs_path = rel if os.path.isabs(rel) else os.path.join(_here, rel)
        text = ""
        if os.path.isfile(abs_path):
            try:
                result, _ = eng(abs_path)
                if result:
                    text = "\n".join(str(x[1]) for x in result if len(x) > 1 and x[1])
            except OSError:
                text = ""
        text = _normalize_whitespace(text).strip()
        if OCR_MAX_CHARS > 0:
            text = text[:OCR_MAX_CHARS]
        rows[i] = {**rec, "text": text, "_ocr_attempted": True}
        n_fill += 1
        print(f"OCR {rel}: {len(text)} chars", flush=True)
        _write_blocks(BLOCKS_JSONL, rows)

    print(f"Updated {BLOCKS_JSONL} (filled {n_fill} image blocks)", flush=True)


if __name__ == "__main__":
    main()
