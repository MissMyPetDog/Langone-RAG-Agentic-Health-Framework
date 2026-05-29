#!/usr/bin/env bash
# CPU ?? ?? ?? ??: multimodal_embed? ??? 1?? ?? ??? vectors_multimodal.jsonl ??.
# ??: ./embed_multimodal_resume.sh 0   # alpha=0.0 ????
#       ./embed_multimodal_resume.sh 35  # alpha=0.35 ??? ???? (?? prune_multimodal_vectors.py --strip-images)
set -euo pipefail
_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$_here"
export PYTHONPATH="${_here}/.venv/lib/python3.10/site-packages"
export LD_LIBRARY_PATH="/gpfs/share/apps/python/gpu/3.10.6/lib:/gpfs/share/apps/python/cpu/3.10.6/lib:${LD_LIBRARY_PATH:-}"

ALPHA_TAG="${1:-0}"
if [[ "$ALPHA_TAG" == "35" ]]; then
  OCR_CLIP_FUSION_ALPHA=0.35
else
  OCR_CLIP_FUSION_ALPHA=0.0
fi

TARGET="$(.venv/bin/python - <<'PY'
import json, os

root = os.getcwd()
linked = {}
with open(os.path.join(root, "data/linked_chunks.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        linked[r["chunk_id"]] = r["modality"]
need = set()
with open(os.path.join(root, "data/chunks.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        c = json.loads(line)
        cid = c.get("chunk_id")
        if not cid or cid not in linked:
            continue
        m = linked[cid]
        if m == "table" and (c.get("text") or "").strip():
            need.add(cid)
        elif m == "image" and c.get("asset_path"):
            ap = c["asset_path"]
            p = ap if os.path.isabs(ap) else os.path.join(root, ap)
            if os.path.isfile(p):
                need.add(cid)
print(len(need))
PY
)"

LOG="${_here}/_embed_multimodal_${ALPHA_TAG}.log"
echo "$(date -Is) start TARGET=${TARGET} OCR_CLIP_FUSION_ALPHA=${OCR_CLIP_FUSION_ALPHA}" | tee -a "$LOG"
while true; do
  n="$(wc -l < data/vectors_multimodal.jsonl)"
  echo "$(date -Is) vectors lines=${n} / ${TARGET}" | tee -a "$LOG"
  if [[ "$n" -ge "$TARGET" ]]; then
    echo "$(date -Is) done" | tee -a "$LOG"
    break
  fi
  INCREMENTAL=1 BATCH_SIZE=1 MULTIMODAL_IMAGE_LIMIT=1 OCR_CLIP_FUSION_ALPHA="${OCR_CLIP_FUSION_ALPHA}" \
    .venv/bin/python -u multimodal_embed.py 2>&1 | tee -a "$LOG" || true
done
wc -l data/vectors_multimodal.jsonl | tee -a "$LOG"
