# Vision vs Text-only 기여도 리포트

- **생성일**: 2026-04-21
- **케이스**: `CASE_{02,03,05,06,07,08,10,17}` (paired, N = 8)
- **비교 방향**: `--text-only` (baseline) → `--vision` (pixels + OCR). Δ = Vision − Text-only.
- **공통 조건**: 동일 질의, 동일 필터(TOC/front-matter/bio-list), 동일 system prompt, `gpt-4o`
- **집계 스크립트**: `scripts/reports/vision_two_way.py`
- **산출물**: `outputs/CASE_NN.md` (vision), `outputs/CASE_NN_textOnly.md`

---

## 1. Setup

1. **코퍼스**: PMID 23499048 (KDIGO 2012 AKI Clinical Practice Guideline) 단일 논문. 필터 후 text 1240 / image 23 chunks. 의미있는 figure는 p12의 *stage-based management of AKI* flowchart 1장이 사실상 유일.

2. **세 가지 모드** (`generate.py`):

   | 모드 | OCR 텍스트 | 이미지 픽셀 |
   |---|---|---|
   | `--vision` | ✅ context 포함 | ✅ `image_url` 첨부 |
   | default | ✅ context 포함 | ❌ |
   | `--text-only` | ❌ | ❌ |

   본 리포트는 **Vision vs Text-only** 양 끝값만 비교. Default(OCR-only 중간값)는 3원 분석에서 다룸.

3. **선정 기준**: 전체 20 케이스 중 retrieval top-5에 image chunk를 포함하는 parent가 등장한 8개만 대상.

---

## 2. 측정 지표

| 지표 | 정의 |
|------|------|
| `word_count` | 답변 본문 단어 수 |
| `distinct_cite` | 답변이 인용한 distinct parent_block_id 수 |
| `num_hits` | `NN.N (mg/dL\|mmHg\|mL/kg/h\|%\|…)` 형태의 verbatim 수치 개수 |
| `signal_hits` | `Hgb/SpO2/UO/Cr/MAP/sepsis/…` 등 환자 관련 키워드 매치 수 |
| `figure_explicit` | 본문에 `Figure N / .png / flowchart / diagram / axes` 등 **표면 문구** 언급 수 |
| **`image_parent_cite`** | 답변이 인용한 parent 중 image chunk를 포함하는 parent 개수 — "figure의 **간접** 인용" |
| `ocr_borrow` | 답변의 5-gram 중 그 케이스가 retrieve한 image chunk의 OCR 텍스트와 겹치는 개수 |

> **왜 figure 지표를 세 개로 쪼갰나**: LLM은 "Figure 4"라고 말하지 않아도, 해당 parent_block_id를 인용하거나 OCR 텍스트를 paraphrase해서 figure를 쓸 수 있다. 표면 문구만 보면 기여가 과소평가된다.

---

## 3. 결과

### 3.1 Retrieval 독립성

`--text-only`는 retrieval 이후 단계만 바꾸므로 top-5 parent는 거의 동일해야 한다.

| CASE | top-5 공통 | | CASE | top-5 공통 |
|------|-----------:|-|------|-----------:|
| 02 | 3 / 5 | | 08 | 3 / 5 |
| 03 | 3 / 5 | | 10 | 4 / 5 |
| 05 | 3 / 5 | | 17 | 4 / 5 |
| 06 | 3 / 5 | | **평균** | **3.38 / 5** |
| 07 | 4 / 5 | |      |            |

차이는 retrieval query 생성 단계(LLM이 환자 텍스트로 query 문장 합성)의 stochasticity에서 발생. text-only 플래그 자체가 retrieval을 바꾸지 않음.

### 3.2 집계 메트릭 (μ ± sd, N = 8)

| 지표 | Text-only | Vision | Δ (V − T) |
|------|-----------|--------|----------:|
| word_count | **480 ± 41** | 369 ± 58 | **−111 (−23 %)** |
| distinct_cite | **3.25 ± 0.43** | 1.75 ± 0.97 | **−1.50** |
| num_hits | 0.62 ± 1.32 | 0.88 ± 1.17 | +0.25 |
| signal_hits | 9.12 ± 4.91 | 7.50 ± 2.69 | −1.62 |
| figure_explicit | 0.00 | 0.00 | 0.00 |
| **image_parent_cite** | 0.38 ± 0.48 | **1.00 ± 0.00** | **+0.62** |
| ocr_borrow (5-gram) | 0.00 | 0.25 ± 0.66 | +0.25 |

### 3.3 방향 일치 (Δ = T − V 부호, "텍스트온리가 비전보다 큰 케이스 수")

| 지표 | T > V | T = V | T < V |
|------|------:|------:|------:|
| word_count | **8 / 8** | 0 | 0 |
| distinct_cite | **7 / 8** | 0 | 1 |
| image_parent_cite | 0 | 3 | **5** |
| signal_hits | 3 | 2 | 3 |
| num_hits | 2 | 4 | 2 |
| figure_explicit | 0 | 8 | 0 |
| ocr_borrow | 0 | 7 | 1 |

### 3.4 케이스별 핵심 변화 (T → V)

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

### 3.5 답변 유사도 (paired 5-gram Jaccard)

| CASE | Jaccard | | CASE | Jaccard |
|------|--------:|-|------|--------:|
| 02 | 0.007 | | 08 | 0.014 |
| 03 | 0.005 | | 10 | 0.028 |
| 05 | 0.007 | | 17 | 0.024 |
| 06 | 0.024 | | **평균** | **0.016** |
| 07 | 0.015 | |      |         |

평균 0.016 = "사실상 다른 텍스트". 이미지 chunk 유무가 답변을 **체계적으로** 바꾼다.

---

## 4. 해석 (T → V 관점: "vision을 켜면 어떻게 되나")

### 4.1 Vision 켜면 답변이 짧아진다 (8/8)

- word_count: **480 → 369 (−23 %)**, **8/8** 케이스에서 T > V.
- 유일한 예외 없음. 가장 일관된 효과.

### 4.2 Vision 켜면 인용 다양성이 줄어든다 (7/8)

- distinct_cite: **3.25 → 1.75 (−1.5)**, **7/8** 에서 T > V (CASE_07만 예외).
- 답변이 여러 parent를 엮는 대신 한두 parent에 집중한다.

### 4.3 Vision 켜면 image-bearing parent 인용이 늘어난다 (5/8, 나머지는 동률)

- image_parent_cite: **0.38 → 1.00 (+0.62)**, 방향 T<V 5건 / 동률 3건 / T>V **0건**.
- 즉 Vision 답변은 **8/8 모두** image-bearing parent(주로 p12 KDIGO management flowchart)를 인용한다.
- Text-only도 3/8에서 p12를 인용(해당 parent에 text chunk도 있으므로) — 다만 빈도 낮음.
- **"LLM이 figure를 안 쓴다"는 해석은 틀림**: "Figure 4"라고 쓰지 않을 뿐, parent_block_id로 간접 인용한다.

### 4.4 Vision 켜도 OCR 텍스트를 verbatim 재사용하진 않는다

- ocr_borrow: Text-only 0 → Vision 0.25 (CASE_03 2건 + 나머지 0).
- LLM은 OCR 조각("Discontinue all nephrotoxic agents… Ensure volume status…")을 자체 어휘로 paraphrase한다.
- Figure는 **conceptual anchor** 역할 — "이 parent가 종합 관리 요약"이라는 신호로 기능하고, 표면은 재작성됨.

### 4.5 Numeric / patient-signal은 모드 효과 불명확

- 방향 2-4-2 (num) / 3-2-3 (signal) 거의 대칭. 분산이 커서(signal sd 4.91) 평균 차이가 묻힘.
- "Vision이 환자 수치를 더 잘 인용한다"는 가설은 **지지받지 못함**.

### 4.6 메커니즘 가설

- image-bearing parent(특히 p12 flowchart)가 LLM에 "종합 관리 요약"으로 강하게 어필
- Vision 켜면 그 parent에 citation이 집중 (§4.3 image_parent_cite ↑)
- 그 결과 다른 text parent를 덜 인용하고(§4.2 cite ↓), 전체 답변도 짧아짐(§4.1 words ↓)
- 세 관찰은 같은 메커니즘의 표현형

### 4.7 Pixel의 marginal 기여는 이 실험으로 분리 불가

- 양 끝값만 비교했으므로 pixel 효과와 OCR 효과가 섞여 있음.
- 중간값(default = OCR-only) 추가 시:
  - Vision − default = pixel marginal
  - default − text-only = OCR marginal

---

## 5. 한계

1. **N = 8**: 통계적 검정력 낮음.
2. **단일 논문 코퍼스**: 의미있는 figure 1장(p12). vision 잠재 효용 평가에 근본적으로 부족.
3. **Noise floor 미측정**: 동일 플래그 N회 반복 실행으로 얻는 stochastic noise baseline을 비교하지 않음. Jaccard 0.016 / 방향 일치가 "순수 LLM 재생성 분산" 대비 얼마나 큰지 엄밀히 분리 불가.
4. **OCR vs pixel 미분리**: 3원 비교 필요.
5. **평가 지표**: Jaccard는 token overlap 기반. "다른 어휘, 같은 임상 논지"는 놓침.

---

## 6. 권고

1. **2-way만 보고 default를 `--text-only`로 단정하지 말 것**
   - Vision은 figure를 실제로 근거로 쓰고 있음(§4.1).
   - Text-only의 답변이 더 길고 다양하지만, 그 diversity가 **Vision이 놓친 실근거**인지 **Vision이 정확히 pruning한 filler**인지는 본 실험만으로 구분 불가.

2. **3원 비교 (다음 단계)**
   - 동일 8 케이스에 default(OCR-only) 8회 추가 실행 → Vision / OCR-only / Text-only의 pixel·OCR marginal 분리.

3. **Vision 평가 upgrade 선결 조건**
   - 플롯·알고리즘 트리가 많은 논문 추가 (p12 같은 flowchart 단일에 의존하지 않도록).
   - system prompt에 figure 인용 강제 규칙 추가 — 예: *"For any attached figure, reproduce its key axis labels or flow step in ≤1 sentence and cite the parent_block_id."*
   - OCR이 틀리고 pixel만 맞는 케이스(혹은 반대) 설계해 pure vision signal 측정.

4. **Noise floor 측정**
   - 동일 플래그로 각 케이스 N회 재실행해 V↔V / T↔T Jaccard 분포를 얻고, V↔T 페어 차이와 비교.

5. **문서화 / 운영**
   - 용도별 default 가이드:
     - 빠른 multi-source 요약 → `--text-only`
     - 관리 프로토콜 정리 → `--vision`
   - 코퍼스 확장 전까지 본 리포트를 baseline으로 보존, 확장 후 delta 측정의 기준으로 사용.

---

## 7. 재현

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
