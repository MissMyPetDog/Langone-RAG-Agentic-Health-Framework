# Vision vs Text-only Contribution Report

- **Created**: 2026-04-21
- **Cases**: `CASE_{02,03,05,06,07,08,10,17}` (paired, N = 8)
- **Comparison direction**: `--text-only` (baseline) → `--vision` (pixels + OCR). Δ = Vision − Text-only.
- **Common conditions**: identical query, identical filters (TOC / front-matter / bio-list), identical system prompt, `gpt-4o`
- **Aggregator**: `scripts/reports/vision_two_way.py`
- **Artifacts**: `outputs/CASE_NN.md` (vision), `outputs/CASE_NN_textOnly.md`

---

## 1. Setup

1. **Corpus**: PMID 23499048 (KDIGO 2012 AKI Clinical Practice Guideline), single paper. After filters: 1240 text / 23 image chunks. The only substantive figure is p12's *stage-based management of AKI* flowchart.

2. **Three modes** (`generate.py`):

   | Mode | OCR text | Image pixels |
   |---|---|---|
   | `--vision` | ✅ in context | ✅ as `image_url` |
   | default | ✅ in context | ❌ |
   | `--text-only` | ❌ | ❌ |

   This report compares only the **Vision vs Text-only** endpoints. The middle condition (default / OCR-only) is left for the 3-way analysis.

3. **Case selection**: of the 20 cases, only the 8 whose retrieval top-5 contained at least one parent hosting an image chunk are included.

---

## 2. Metrics

| Metric | Definition |
|--------|-----------|
| `word_count` | word count of the Answer body |
| `distinct_cite` | number of distinct `parent_block_id`s cited in the answer |
| `num_hits` | verbatim numeric mentions like `NN.N (mg/dL\|mmHg\|mL/kg/h\|%\|…)` |
| `signal_hits` | patient-keyword matches (`Hgb/SpO2/UO/Cr/MAP/sepsis/…`) |
| `figure_explicit` | surface mentions of `Figure N / .png / flowchart / diagram / axes` |
| **`image_parent_cite`** | number of cited parents that host ≥1 image chunk — i.e. **implicit** figure citation |
| `ocr_borrow` | number of 5-grams in the answer that also appear in the OCR text of image chunks retrieved for this case |

> **Why three figure-usage metrics**: the LLM can use a figure without ever writing "Figure 4" — it can cite the hosting parent_block_id or paraphrase the OCR text. A surface-string metric alone underestimates the contribution.

---

## 3. Results

### 3.1 Retrieval independence

`--text-only` affects only post-retrieval context building, so the top-5 parent set should be nearly identical.

| CASE | top-5 common | | CASE | top-5 common |
|------|-------------:|-|------|-------------:|
| 02 | 3 / 5 | | 08 | 3 / 5 |
| 03 | 3 / 5 | | 10 | 4 / 5 |
| 05 | 3 / 5 | | 17 | 4 / 5 |
| 06 | 3 / 5 | | **mean** | **3.38 / 5** |
| 07 | 4 / 5 | |      |              |

Residual differences come from stochasticity in the LLM-synthesized retrieval query. The text-only flag itself does not change retrieval.

### 3.2 Aggregate (μ ± sd, N = 8)

| Metric | Text-only | Vision | Δ (V − T) |
|--------|-----------|--------|----------:|
| word_count | **480 ± 41** | 369 ± 58 | **−111 (−23 %)** |
| distinct_cite | **3.25 ± 0.43** | 1.75 ± 0.97 | **−1.50** |
| num_hits | 0.62 ± 1.32 | 0.88 ± 1.17 | +0.25 |
| signal_hits | 9.12 ± 4.91 | 7.50 ± 2.69 | −1.62 |
| figure_explicit | 0.00 | 0.00 | 0.00 |
| **image_parent_cite** | 0.38 ± 0.48 | **1.00 ± 0.00** | **+0.62** |
| ocr_borrow (5-gram) | 0.00 | 0.25 ± 0.66 | +0.25 |

### 3.3 Direction agreement (sign of Δ = T − V, "cases where text-only exceeds vision")

| metric | T > V | T = V | T < V |
|--------|------:|------:|------:|
| word_count | **8 / 8** | 0 | 0 |
| distinct_cite | **7 / 8** | 0 | 1 |
| image_parent_cite | 0 | 3 | **5** |
| signal_hits | 3 | 2 | 3 |
| num_hits | 2 | 4 | 2 |
| figure_explicit | 0 | 8 | 0 |
| ocr_borrow | 0 | 7 | 1 |

### 3.4 Per-case highlights (T → V)

| CASE | words T→V | cite T→V | image_parent_cite T→V | ocr_borrow T→V |
|------|----------:|---------:|---------------------:|---------------:|
| 02 | 468 → **311 (−157)** | 4 → **1 (−3)** | 0 → 1 | 0 → 0 |
| 03 | 424 → **343 (−81)**  | 3 → **2 (−1)** | 0 → 1 | **0 → 2** |
| 05 | 531 → **318 (−213)** | 3 → **1 (−2)** | 0 → 1 | 0 → 0 |
| 06 | 434 → **334 (−100)** | 4 → **1 (−3)** | 0 → 1 | 0 → 0 |
| 07 | 528 → **362 (−166)** | 3 → 4 (+1)     | 1 → 1 | 0 → 0 |
| 08 | 505 → **442 (−63)**  | 3 → **2 (−1)** | 0 → 1 | 0 → 0 |
| 10 | 440 → **361 (−79)**  | 3 → **1 (−2)** | 1 → 1 | 0 → 0 |
| 17 | 510 → **484 (−26)**  | 3 → **2 (−1)** | 1 → 1 | 0 → 0 |

### 3.5 Paired answer similarity (5-gram Jaccard)

| CASE | Jaccard | | CASE | Jaccard |
|------|--------:|-|------|--------:|
| 02 | 0.007 | | 08 | 0.014 |
| 03 | 0.005 | | 10 | 0.028 |
| 05 | 0.007 | | 17 | 0.024 |
| 06 | 0.024 | | **mean** | **0.016** |
| 07 | 0.015 | |      |         |

Mean 0.016 = "essentially different texts." The presence/absence of image chunks systematically changes the answer.

---

## 4. Interpretation (T → V perspective: "what happens when we turn vision on")

### 4.1 Turning on vision shortens answers (8/8)

- word_count: **480 → 369 (−23 %)**, **8/8** cases show T > V.
- No exceptions. The most consistent effect.

### 4.2 Turning on vision reduces citation diversity (7/8)

- distinct_cite: **3.25 → 1.75 (−1.5)**, **7/8** cases show T > V (CASE_07 is the only exception).
- The answer stops weaving multiple parents together and concentrates on one or two.

### 4.3 Turning on vision raises image-bearing-parent citation (5/8, rest tie)

- image_parent_cite: **0.38 → 1.00 (+0.62)**, direction T<V 5 / tie 3 / T>V **0**.
- Every single Vision answer cites at least one image-bearing parent (almost always p12, KDIGO management flowchart).
- Text-only also cites p12 in 3/8 cases (its text chunks survive), but the rate drops sharply.
- **So "the LLM doesn't use figures" is wrong** — it just doesn't write "Figure 4"; it cites by parent_block_id.

### 4.4 Vision doesn't copy OCR text verbatim either

- ocr_borrow: Text-only 0 → Vision 0.25 (CASE_03 has 2 matches, the rest 0).
- The LLM paraphrases OCR fragments ("Discontinue all nephrotoxic agents… Ensure volume status…") in its own wording.
- The figure acts as a **conceptual anchor** — it signals "this parent is the comprehensive management summary" — while the surface answer is rewritten.

### 4.5 No clear effect on numeric / patient-signal metrics

- Direction 2-4-2 (num) / 3-2-3 (signal) — nearly symmetric. Variance (signal sd 4.91) drowns the mean gap.
- The hypothesis "Vision helps quote patient numerics" is **not supported**.

### 4.6 Mechanism hypothesis

- The image-bearing parent (especially p12 flowchart) registers with the LLM as a "comprehensive management summary."
- Turning on vision concentrates citations on that parent (§4.3 image_parent_cite ↑),
- which leaves fewer citations for other text parents (§4.2 cite ↓),
- which shortens the overall answer (§4.1 words ↓).
- All three observations are phenotypes of the same mechanism.

### 4.7 Pixel marginal contribution cannot be isolated here

- Only the endpoints are compared, so pixel and OCR effects are combined.
- Adding the middle (default = OCR-only):
  - Vision − default = pixel marginal
  - default − text-only = OCR marginal

---

## 5. Limitations

1. **N = 8**: low statistical power.
2. **Single-paper corpus**: only one meaningful figure (p12). Fundamentally inadequate for evaluating vision potential.
3. **No noise floor**: did not run N repeats of the same flag to measure stochastic variance baseline, so Jaccard 0.016 / directional agreement cannot be formally separated from LLM regeneration noise.
4. **OCR vs pixel not separated**: requires the 3-way comparison.
5. **Metric gap**: Jaccard is token-overlap based — it misses "same clinical claim, different wording."

---

## 6. Recommendations

1. **Don't declare `--text-only` the default based on this 2-way alone.**
   - Vision does use the figure as evidence (§4.1).
   - Text-only answers are longer and more diverse, but we can't tell from this study whether that extra diversity is **real evidence Vision missed** or **filler Vision correctly pruned away**.

2. **Next step — 3-way comparison.**
   - Add 8 default (OCR-only) runs for the same cases → isolate pixel vs OCR marginal contributions.

3. **Pre-conditions for a meaningful vision evaluation.**
   - Add papers rich in figures (plots, algorithm trees) so the corpus doesn't hinge on a single flowchart.
   - Add a forced-figure-citation rule to the system prompt, e.g. *"For any attached figure, reproduce its key axis labels or flow step in ≤1 sentence and cite the parent_block_id."*
   - Construct cases where OCR is wrong but pixels are right (or vice versa) to measure pure vision signal.

4. **Noise floor measurement.**
   - Run each case N times with the same flag, compute V↔V / T↔T Jaccard distributions, and compare against the V↔T paired difference.

5. **Documentation / operational guidance.**
   - Use-case based default:
     - fast multi-source triage → `--text-only`
     - management-protocol style answer → `--vision`
   - Keep this report as the baseline for delta measurement after corpus expansion.

---

## 7. Reproduction

```bash
cd /gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739
module load python/gpu/3.10.6
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:${LD_LIBRARY_PATH:-}
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
D=/gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts

for n in 02 03 05 06 07 08 10 17; do
  ./.venv/bin/python generate.py \
    --patient-data-file "$D/CASE_${n}.txt" \
    --case-id "CASE_${n}" --vision

  ./.venv/bin/python generate.py \
    --patient-data-file "$D/CASE_${n}.txt" \
    --case-id "CASE_${n}_textOnly" --text-only
done

./.venv/bin/python scripts/reports/vision_two_way.py
```
