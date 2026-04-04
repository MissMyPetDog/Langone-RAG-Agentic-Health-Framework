"""
Parse PDFs/TXT into page-level text and image blocks.

Inputs: assets.jsonl (또는 data/assets.jsonl)
Output: data/blocks.jsonl
"""
from __future__ import annotations

import sys
import os as _os

# venv site-packages 최우선 (시스템 typing_extensions 등과 충돌 방지)
_here = _os.path.dirname(_os.path.abspath(__file__))
_venv_site = _os.path.join(_here, ".venv", "lib", "python3.10", "site-packages")
if _os.path.isdir(_venv_site):
    if _venv_site not in sys.path:
        sys.path.insert(0, _venv_site)
    _sys_site = _os.path.join(_os.path.sep + "gpfs", "share", "apps", "python")
    sys.path = [p for p in sys.path if _sys_site not in p] + [p for p in sys.path if _sys_site in p]

import json
import os
from typing import Dict, Iterable, List, Tuple

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

ASSETS_JSONL = "assets.jsonl"
DATA_ASSETS_JSONL = "data/assets.jsonl"
BLOCKS_JSONL = "data/blocks.jsonl"
MAX_BLOCK_CHARS = 1600
OCR_ON_IMAGES = os.environ.get("OCR_ON_IMAGES", "1").lower() in ("1", "true", "yes")
OCR_MAX_CHARS = int(os.environ.get("OCR_MAX_CHARS", "4000"))
OCR_BACKEND = os.environ.get("OCR_BACKEND", "auto").strip().lower()  # auto|rapidocr|tesseract|easyocr
EASYOCR_LANGS = [
    s.strip() for s in os.environ.get("EASYOCR_LANGS", "en").split(",") if s.strip()
]
# 쉼표 구분 doc_id만 재파싱하고, 기존 blocks.jsonl에서 해당 doc 블록을 제거한 뒤 병합 (전체 OCR 재실행 방지)
_PARSE_DOC_IDS_RAW = os.environ.get("PARSE_DOC_IDS", "").strip()
PARSE_DOC_IDS: frozenset[str] | None = (
    frozenset(s.strip() for s in _PARSE_DOC_IDS_RAW.split(",") if s.strip())
    if _PARSE_DOC_IDS_RAW
    else None
)

try:
    import pytesseract
except Exception:
    pytesseract = None  # type: ignore[assignment]
try:
    import easyocr
except Exception:
    easyocr = None  # type: ignore[assignment]
try:
    from rapidocr_onnxruntime import RapidOCR as _RapidOCRCls
except Exception:
    _RapidOCRCls = None  # type: ignore[misc, assignment]

_OCR_WARNED = False
_EASYOCR_READER = None
_EASYOCR_DL_PATCHED = False
_RAPID_OCR_ENGINE = None


def _get_rapid_ocr():
    global _RAPID_OCR_ENGINE
    if _RapidOCRCls is None:
        return None
    if _RAPID_OCR_ENGINE is None:
        _RAPID_OCR_ENGINE = _RapidOCRCls()
    return _RAPID_OCR_ENGINE


def _ensure_easyocr_dataloader_cpu_safe() -> None:
    """CPU 환경에서 EasyOCR recognition DataLoader의 pin_memory=True가 멈춤을 유발하는 경우가 있어 끈다."""
    global _EASYOCR_DL_PATCHED
    if _EASYOCR_DL_PATCHED or easyocr is None:
        return
    import torch.utils.data as tud

    _orig = tud.DataLoader.__init__

    def _init(self, *args, **kwargs):
        kwargs["pin_memory"] = False
        return _orig(self, *args, **kwargs)

    tud.DataLoader.__init__ = _init  # type: ignore[method-assign, assignment]
    _EASYOCR_DL_PATCHED = True


def _iter_assets(path: str) -> Iterable[Dict]:
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _normalize_whitespace(text: str) -> str:
    """단락 내부 단일 개행은 공백으로 합치고, 빈 줄은 단락 구분으로 유지."""
    lines = text.splitlines()
    out_lines: List[str] = []
    buf: List[str] = []
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
    # 빈 줄 두 개 기준으로 단락 구분 유지
    return "\n\n".join(line for line in out_lines if line != "" or (line == "" and out_lines))


def _split_text_blocks(page_text: str, doc_id: str, page_num: int) -> List[Dict]:
    """페이지 텍스트를 MAX_BLOCK_CHARS 기준으로 t0, t1, ... 블록으로 나눔."""
    text = _normalize_whitespace(page_text or "")
    if not text:
        return []
    blocks: List[Dict] = []
    start = 0
    idx = 0
    n = len(text)
    while start < n:
        end = min(start + MAX_BLOCK_CHARS, n)
        # 문장 끝 근처에서 자르기 시도 (.?!)
        cut = end
        for back in range(200):
            pos = end - back
            if pos <= start + 200:
                break
            if text[pos - 1] in ".?!":
                cut = pos
                break
        chunk = text[start:cut].strip()
        if chunk:
            block_id = f"{doc_id}_p{page_num}_t{idx}"
            blocks.append(
                {
                    "block_id": block_id,
                    "doc_id": doc_id,
                    "modality": "text",
                    "page": page_num,
                    "text": chunk,
                }
            )
            idx += 1
        start = cut
    return blocks


def _extract_ocr_text(image_path: str) -> str:
    """이미지 경로에서 OCR 텍스트 추출. auto 시 RapidOCR → Tesseract → EasyOCR 순."""
    global _OCR_WARNED, _EASYOCR_READER
    if not OCR_ON_IMAGES:
        return ""

    order: List[str]
    if OCR_BACKEND == "rapidocr":
        order = ["rapid"]
    elif OCR_BACKEND == "tesseract":
        order = ["tesseract"]
    elif OCR_BACKEND == "easyocr":
        order = ["easy"]
    else:
        order = []
        if _RapidOCRCls is not None:
            order.append("rapid")
        if pytesseract is not None:
            order.append("tesseract")
        if easyocr is not None:
            order.append("easy")

    if not order:
        if not _OCR_WARNED:
            print(
                "OCR disabled: install rapidocr-onnxruntime and/or pytesseract+tessdata and/or easyocr.",
                flush=True,
            )
            _OCR_WARNED = True
        return ""

    def _clip(s: str) -> str:
        s = _normalize_whitespace(s).strip()
        if OCR_MAX_CHARS > 0 and len(s) > OCR_MAX_CHARS:
            return s[:OCR_MAX_CHARS]
        return s

    rgb = None
    ocr_arr = None

    for b in order:
        text = ""
        if b == "rapid":
            eng = _get_rapid_ocr()
            if eng is None:
                continue
            try:
                result, _ = eng(image_path)
                if result:
                    text = "\n".join(str(x[1]) for x in result if len(x) > 1 and x[1])
            except Exception:
                text = ""
            if text.strip():
                return _clip(text)

        elif b == "tesseract":
            if pytesseract is None:
                continue
            try:
                if rgb is None:
                    with Image.open(image_path) as im:
                        rgb = im.convert("RGB").copy()
                text = pytesseract.image_to_string(rgb)
            except Exception:
                text = ""
            if text.strip():
                return _clip(text)

        elif b == "easy":
            if easyocr is None:
                continue
            try:
                if rgb is None:
                    with Image.open(image_path) as im:
                        rgb = im.convert("RGB").copy()
                if ocr_arr is None:
                    ocr_arr = np.asarray(rgb)
                if _EASYOCR_READER is None:
                    _ensure_easyocr_dataloader_cpu_safe()
                    _EASYOCR_READER = easyocr.Reader(EASYOCR_LANGS, gpu=False)
                parts = _EASYOCR_READER.readtext(
                    ocr_arr,
                    detail=0,
                    paragraph=False,
                    workers=0,
                    batch_size=1,
                    canvas_size=1600,
                    mag_ratio=0.85,
                )
                text = "\n".join(parts) if parts else ""
            except Exception:
                text = ""
            if text.strip():
                return _clip(text)

    return ""


def _extract_images(doc: fitz.Document, doc_id: str, out_dir: str) -> List[Dict]:
    """페이지별 figure 이미지를 data/raw/{doc_id}/page_{page}_fig_{k}.ext 로 저장."""
    os.makedirs(out_dir, exist_ok=True)
    blocks: List[Dict] = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_num = page_index + 1
        images = page.get_images(full=True)
        for fig_idx, img in enumerate(images):
            xref = img[0]
            try:
                base = doc.extract_image(xref)
            except Exception:
                continue
            img_bytes = base["image"]
            ext = base.get("ext", "png")
            rel_path = os.path.join("data", "raw", doc_id, f"page_{page_num}_fig_{fig_idx}.{ext}")
            abs_path = os.path.join(_here, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "wb") as out:
                out.write(img_bytes)
            block_id = f"{doc_id}_p{page_num}_fig_{fig_idx}"
            ocr_text = _extract_ocr_text(abs_path)
            blocks.append(
                {
                    "block_id": block_id,
                    "doc_id": doc_id,
                    "modality": "image",
                    "page": page_num,
                    "asset_path": rel_path,
                    "caption": None,
                    "text": ocr_text,
                }
            )
    return blocks


def _parse_pdf(doc_id: str, path: str) -> List[Dict]:
    print(f"Parsing PDF for doc_id={doc_id}: {path}", flush=True)
    try:
        doc = fitz.open(path)
    except Exception as e:
        print(f"Failed to open {path}: {e}")
        return []

    blocks: List[Dict] = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_num = page_index + 1
        text = page.get_text("text")
        blocks.extend(_split_text_blocks(text, doc_id, page_num))

    # 이미지 추출
    raw_dir = os.path.join(_here, "data", "raw", doc_id)
    blocks.extend(_extract_images(doc, doc_id, raw_dir))
    doc.close()
    return blocks


def main() -> None:
    # assets.jsonl 우선, 없으면 data/assets.jsonl 사용
    assets_path = ASSETS_JSONL if os.path.isfile(ASSETS_JSONL) else DATA_ASSETS_JSONL
    if not os.path.isfile(assets_path):
        print(f"No assets file found at {ASSETS_JSONL} or {DATA_ASSETS_JSONL}")
        raise SystemExit(1)

    all_blocks: List[Dict] = []
    for asset in _iter_assets(assets_path):
        doc_id = asset.get("doc_id")
        kind = asset.get("kind", "")
        path = asset.get("path")
        if not doc_id or not path:
            continue
        if PARSE_DOC_IDS is not None and doc_id not in PARSE_DOC_IDS:
            continue
        # 현재는 PDF 위주. TXT 등 다른 형식이 생기면 분기 추가.
        if not os.path.isfile(path):
            # data/raw/{doc_id}/fulltext.pdf 형태로도 시도
            alt = os.path.join("data", "raw", doc_id, "fulltext.pdf")
            if os.path.isfile(alt):
                path = alt
            else:
                print(f"Missing asset file for doc_id={doc_id}: {path}")
                continue
        if kind.lower() == "pdf" or path.lower().endswith(".pdf"):
            all_blocks.extend(_parse_pdf(doc_id, path))
        else:
            # 기타 형식은 일단 텍스트로 시도
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                block_id = f"{doc_id}_p1_t0"
                all_blocks.append(
                    {
                        "block_id": block_id,
                        "doc_id": doc_id,
                        "modality": "text",
                        "page": 1,
                        "text": _normalize_whitespace(text),
                    }
                )
            except Exception:
                print(f"Skipping unsupported asset for doc_id={doc_id}: {path}")

    if PARSE_DOC_IDS is not None and os.path.isfile(BLOCKS_JSONL):
        kept: List[Dict] = []
        with open(BLOCKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("doc_id") in PARSE_DOC_IDS:
                    continue
                kept.append(rec)
        all_blocks = kept + all_blocks

    os.makedirs(os.path.dirname(BLOCKS_JSONL) or ".", exist_ok=True)
    with open(BLOCKS_JSONL, "w", encoding="utf-8") as out:
        for rec in all_blocks:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_blocks)} blocks to {BLOCKS_JSONL}")


if __name__ == "__main__":
    main()

