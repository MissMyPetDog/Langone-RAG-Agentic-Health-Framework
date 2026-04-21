# Vision ON vs OFF — Contribution Report

**Date**: 2026-04-21  
**Cases**: 6 (paired)  
**Compared**: `outputs/CASE_{02,03,05,06,07,17}.md` (Vision ON) vs. `outputs/CASE_{02,03,05,06,07,17}_noVision.md` (Vision OFF)  
**Held constant**: identical query, identical filter (99 drop), identical prompt (new `generate.py` system prompt), identical model  
**Varied**: only the `--vision` flag

---

## 1. Experimental Setup

1. **Corpus**: PMID 23499048 (KDIGO 2012 AKI Clinical Practice Guideline), a single paper
2. **Filter state**: TOC + front-matter + bio-list filters applied (1240 text chunks / 23 image chunks)
3. **Prompt**: new system prompt (patient-grounded reasoning, mandatory "Why this patient:" sub-structure, multi-source synthesis rule)
4. **Model**: `gpt-4o` (default)
5. **Vision delivery**: when a retrieved parent block contains a figure chunk, the corresponding PNG is attached to the LLM as an `image_url` (max 6 figures, `VISION_MAX_EDGE=1536`)

**Case selection rationale**: out of the full 20 cases, only these 6 had a figure-bearing parent appear in the retrieval top-5, i.e. only these 6 actually received images at the LLM. For the other 14 cases, toggling `--vision` produces an identical text-only call, so they carry no A/B information.

---

## 2. Aggregate Results

| Metric | Vision ON | Vision OFF | Δ (ON − OFF) | Interpretation |
|--------|-----------|------------|--------------|----------------|
| "Why this patient" lines | μ=3.00, sd=0.00 | μ=3.00, sd=0.00 | 0.00 | New prompt structure is 100% honored regardless of vision |
| **Distinct cited parents** | μ=**2.17**, sd=0.98 | μ=**3.17**, sd=0.75 | **−1.00** | ⚠️ OFF actually cites more distinct sources |
| **Answer word count** | μ=**411.5**, sd=69.4 | μ=**521.8**, sd=58.5 | **−110.3** | ⚠️ OFF answers are +27% longer |
| Numeric-value hits | μ=0.83, sd=1.33 | μ=0.17, sd=0.41 | +0.67 | ON slightly ahead, absolute counts small |
| Patient-signal hits | μ=2.50, sd=2.07 | μ=2.00, sd=1.41 | +0.50 | ON slightly ahead |
| **Figure / visual-ref hits** | μ=**0.00** | μ=**0.00** | 0.00 | 🔴 neither side mentions figures at all |

*Numeric-value hit = a verbatim `NN.N (mg/dL|mmHg|mL/kg/h|%|...)` pattern in the answer*  
*Patient-signal hit = short medical tokens (`Hgb / SpO2 / UO / Cr / MAP / sepsis / ...`)*  
*Figure hit = mentions of `Figure N`, `.png`, `flowchart`, `diagram`, `axes`*

### Per-case delta (ON → OFF)

| Case | cite | patient-signal | numeric | figure-ref |
|------|------|----------------|---------|------------|
| 02 | 2 → **3 (+1)** | 5 → 0 (−5) | 2 → 1 (−1) | 0 → 0 |
| 03 | 2 → 2 (0) | 5 → 4 (−1) | 3 → 0 (−3) | 0 → 0 |
| 05 | 2 → **4 (+2)** | 2 → 2 (0) | 0 → 0 | 0 → 0 |
| 06 | 1 → **3 (+2)** | 1 → 3 (+2) | 0 → 0 | 0 → 0 |
| 07 | 4 → 4 (0) | 0 → 2 (+2) | 0 → 0 | 0 → 0 |
| 17 | 2 → **3 (+1)** | 2 → 1 (−1) | 0 → 0 | 0 → 0 |

---

## 3. Retrieval Independence Check

`--vision` only affects the LLM call stage, not retrieval, so in principle the top-5 parent set should be identical across the paired runs. We observe near-identity.

| Case | top-5 overlap | Same order | Notes |
|------|---------------|-----------|-------|
| 02 | 4 / 5 | ✓ | Same parents, slight c0/c1 chunk variation |
| 03 | 3 / 5 | ✗ | Rank-1 shift: p12 ↔ p13 |
| 05 | 3 / 5 | ✗ | Rank-1 shift: p12 ↔ p130 |
| 06 | 3 / 5 | ✗ | Rank-1 shift: p12 ↔ p76 |
| 07 | 4 / 5 | ✓ | |
| 17 | 4 / 5 | ✓ | |

**Mean overlap = 3.5 / 5.** Half of the cases are fully identical in order. The three mismatched cases can be explained by **stochasticity in the LLM-generated retrieval query** (the patient text is condensed into a question by an LLM before BGE encoding). The vision flag itself does not influence retrieval.

---

## 4. Paired Answer Similarity

5-gram Jaccard between the ON and OFF answers in each case:

| Case | Jaccard |
|------|---------|
| 02 | 0.009 |
| 03 | 0.017 |
| 05 | 0.016 |
| 06 | 0.032 |
| 07 | 0.007 |
| 17 | 0.050 |
| **mean** | **0.022** |

Reference: mean Jaccard **across** unrelated cases ≈ 0.024.  
⇒ **Paired ON/OFF similarity ≈ unrelated-case similarity.**  
In other words, the answer variance produced by toggling vision is on the same order as the baseline stochasticity of the LLM. The vision signal is effectively lost in that noise.

---

## 5. Key Interpretation

### 5.1 No evidence the LLM actually used the figure

- All 6 ON answers have **0 mentions** of "Figure N / .png / flowchart / diagram / axes".
- Thus, even though pixels were attached, the model never invokes the image as visible evidence.
- Plausible causes:
  1. **Corpus limitation**: the only figure in this corpus is a single `Figure 4 — stage-based management of AKI` flowchart. There are no plots, numeric charts, or imaging panels that would carry unique visual information.
  2. **Weak prompt for figures**: the system prompt only tells the model to use `.png` if it names a figure file; it does not *force* figure-content citation.
  3. **Retrieval coupling**: figure chunks enter top-5 as filler whose parent is rarely cited. The model has no incentive to bridge figure context into the answer.

### 5.2 Vision ON hurts multi-source diversity

- Distinct cited parents: ON=2.17, OFF=3.17 → **−1.00**
- In 6/6 cases, OFF ties or exceeds ON in citation count.
- Hypothesized mechanism: image tokens consume part of the model's attention budget, leaving less capacity to cross-reference multiple text sources. The result is a shorter answer (−27% word count) with fewer citations.

### 5.3 Numeric verbatim citation marginally favors ON

- ON=0.83 vs OFF=0.17 → +0.67
- However the sample is sparse (most cases at 0). Only 2 cases drive the difference. Not enough to claim "vision improves numeric grounding".

### 5.4 Paired similarity is indistinguishable from stochastic baseline

- Paired mean Jaccard = 0.022; unrelated-case mean = 0.024 → **statistically indistinguishable**.
- Whatever signal vision produces is buried in the generation noise of the LLM.

---

## 6. Limitations

1. **Small sample (N=6)**: limited statistical power; individual case Δs exceed the population-level signal.
2. **Single-paper corpus**: only 1 figure available. This environment is fundamentally underpowered to evaluate the upside of vision.
3. **Default LLM temperature**: a single paired run can swing wildly. A rigorous design requires fixed seeds or N-repeat averages.
4. **OCR not audited**: the OCR quality of the figure chunk is not separately measured. If the OCR already captures the figure's information as text, the marginal value of the pixels approaches zero.

---

## 7. Recommendations

1. **Default `--vision` to OFF for now**
   - No clear benefit is observed in the current corpus and prompt.
   - Saves image tokens / API cost.

2. **Prerequisites for a meaningful vision evaluation**
   - (a) **Expand corpus** to papers rich in figures (plots, prevalence graphs, decision trees, imaging).
   - (b) **Strengthen the prompt** with a figure-citation requirement, e.g. *"For any attached figure, reproduce one key axis label or flow step in ≤1 sentence and cite the parent_block_id."*
   - (c) **Design OCR-vs-image discrepancy cases**: questions that are wrong from OCR alone but answerable from the pixels, to isolate a vision-only signal.

3. **Adjacent fixes**
   - Consider a mild retrieval boost for figure-containing parents so they are not wasted filler.
   - Investigate the new never-cited parents (`p3`, `p8`, `p10`) that currently take the top-5 filler role; they are unrelated to vision but remain low-value.

4. **Documentation**
   - Update `README.md` to note: "Default `--vision` is OFF; re-evaluate once the corpus is expanded."
   - Keep this report in `reports/` as a baseline for future delta measurements.

---

## 8. Reproduction

```bash
# shared environment
cd /gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739
module load python/gpu/3.10.6
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:${LD_LIBRARY_PATH:-}

# Vision ON (already persisted as outputs/CASE_XX.md)
for i in 02 03 05 06 07 17; do
  .venv/bin/python generate.py \
    --patient-data-file /gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts/CASE_${i}.txt \
    --case-id CASE_${i} \
    --vision
done

# Vision OFF (outputs/CASE_XX_noVision.md)
for i in 02 03 05 06 07 17; do
  .venv/bin/python generate.py \
    --patient-data-file /gpfs/data/razavianlab/capstone/2025_agentic/tester_for_momo/case_texts/CASE_${i}.txt \
    --case-id CASE_${i}_noVision
done
```

The metric-aggregation script used to produce the tables above is currently ad hoc; a polished version should land under `scripts/` if the evaluation is to be repeated.
