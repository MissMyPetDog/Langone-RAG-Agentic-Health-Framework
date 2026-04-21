# Vision ON vs OFF 기여도 리포트

**생성일**: 2026-04-21  
**케이스 수**: 6 (paired)  
**비교 대상**: `outputs/CASE_{02,03,05,06,07,17}.md` (Vision ON) ↔ `outputs/CASE_{02,03,05,06,07,17}_noVision.md` (Vision OFF)  
**공통 조건**: 동일 질의, 동일 필터(99 drop), 동일 프롬프트(`generate.py` 신규 버전), 동일 모델  
**변수**: `--vision` 플래그만 on/off

---

## 1. 실험 설계

1. **코퍼스**: PMID 23499048 (KDIGO 2012 AKI Clinical Practice Guideline) 단일 논문
2. **필터 상태**: TOC + front-matter + bio-list 필터 적용 (1240 text chunks / 23 image chunks)
3. **프롬프트**: 새 system prompt (patient-grounded reasoning, "Why this patient:" 구조, multi-source 강제)
4. **모델**: `gpt-4o` (기본값)
5. **vision 구현**: retrieval된 parent blocks 중 figure chunk가 있으면 해당 PNG를 `image_url`로 LLM에 첨부 (max 6, VISION_MAX_EDGE=1536)

**선정 근거**: 전체 20 케이스 중 retrieval top-5에 figure chunk 포함 parent가 등장하여 실제로 이미지가 LLM에 전달된 6 케이스만 A/B 비교 대상으로 삼음. 나머지 14개는 vision 플래그 유무와 무관하게 동일한 text-only 호출이므로 비교 의미 없음.

---

## 2. 집계 결과

| 지표 | Vision ON | Vision OFF | Δ (ON − OFF) | 해석 |
|------|----------|------------|--------------|------|
| "Why this patient" 라인 수 | μ=3.00, sd=0.00 | μ=3.00, sd=0.00 | 0.00 | 새 프롬프트 구조는 플래그 무관 100% 준수 |
| **Distinct cited parents** | μ=**2.17**, sd=0.98 | μ=**3.17**, sd=0.75 | **−1.00** | ⚠️ OFF가 multi-source 더 많이 인용 |
| **Answer word count** | μ=**411.5**, sd=69.4 | μ=**521.8**, sd=58.5 | **−110.3** | ⚠️ OFF 답변이 +27% 더 긺 |
| Numeric-value hits | μ=0.83, sd=1.33 | μ=0.17, sd=0.41 | +0.67 | ON 약간 유리, 절대값 작음 |
| Patient-signal hits | μ=2.50, sd=2.07 | μ=2.00, sd=1.41 | +0.50 | ON 약간 유리 |
| **Figure / visual-ref hits** | μ=**0.00** | μ=**0.00** | 0.00 | 🔴 양쪽 모두 figure 언급 전무 |

*Numeric-value hit = `NN.N (mg/dL|mmHg|mL/kg/h|%|...)` 형태의 verbatim 수치*  
*Patient-signal hit = `Hgb / SpO2 / UO / Cr / MAP / sepsis / ...` 등 약자/키워드 매치*  
*Figure hit = `Figure N`, `.png`, `flowchart`, `diagram`, `axes` 매치*

### 케이스별 변화 (ON → OFF)

| CASE | cite | patient-signal | numeric | figure-ref |
|------|------|----------------|---------|------------|
| 02 | 2 → **3 (+1)** | 5 → 0 (−5) | 2 → 1 (−1) | 0 → 0 |
| 03 | 2 → 2 (0) | 5 → 4 (−1) | 3 → 0 (−3) | 0 → 0 |
| 05 | 2 → **4 (+2)** | 2 → 2 (0) | 0 → 0 | 0 → 0 |
| 06 | 1 → **3 (+2)** | 1 → 3 (+2) | 0 → 0 | 0 → 0 |
| 07 | 4 → 4 (0) | 0 → 2 (+2) | 0 → 0 | 0 → 0 |
| 17 | 2 → **3 (+1)** | 2 → 1 (−1) | 0 → 0 | 0 → 0 |

---

## 3. Retrieval 독립성 검증

`--vision`은 retrieval 이후의 LLM 호출 단계에만 개입하므로 이론상 top-5 parent 집합은 동일해야 한다. 실제로도 거의 같음.

| CASE | top-5 공통 parent | 동일 순서 | 비고 |
|------|--------------------|-----------|------|
| 02 | 4 / 5 | ✓ | 한 chunk id의 c0/c1 차이로 재집계 시 동일 |
| 03 | 3 / 5 | ✗ | 1위 p12 ↔ p13 교체 |
| 05 | 3 / 5 | ✗ | 1위 p12 ↔ p130 교체 |
| 06 | 3 / 5 | ✗ | 1위 p12 ↔ p76 교체 |
| 07 | 4 / 5 | ✓ | |
| 17 | 4 / 5 | ✓ | |

**평균 공통 = 3.5 / 5.** 케이스 3/6이 완전 동일 순서. 차이나는 3개는 **retrieval query 생성 단계**(LLM이 환자 텍스트로부터 query 문장 합성)에서 발생하는 **stochasticity** 때문으로 보임. vision 플래그 자체가 retrieval 결과를 바꾸지는 않는다.

---

## 4. 답변 유사도 (paired)

5-gram Jaccard로 vision ON ↔ OFF 페어 답변이 얼마나 다른지 측정.

| CASE | Jaccard |
|------|---------|
| 02 | 0.009 |
| 03 | 0.017 |
| 05 | 0.016 |
| 06 | 0.032 |
| 07 | 0.007 |
| 17 | 0.050 |
| **평균** | **0.022** |

참고: 서로 다른 케이스들 사이의 평균 Jaccard = 0.024.  
⇒ **같은 케이스 on/off 페어 Jaccard ≈ 완전 다른 케이스 간 평균**.  
즉 vision 차이가 만드는 답변 변화의 크기 ≲ LLM의 baseline stochasticity. 시그널이 노이즈에 묻힘.

---

## 5. 핵심 해석

### 5.1 LLM이 figure를 실제로 사용한 증거가 보이지 않는다

- 6/6 ON 답변 모두 "Figure N / .png / flowchart / diagram / axes" 언급 **0건**
- 즉 pixel을 받더라도 답변에 시각 정보를 인용/요약/근거화하지 않음
- 원인 후보:
  1. **코퍼스 문제**: 현재 figure는 `Figure 4 stage-based management of AKI` flowchart 1장뿐. 의미있는 플롯/수치 그림이 부족.
  2. **프롬프트 약함**: system prompt는 "figure filename 언급 시 `.png`" 규칙만 포함, figure 내용 인용을 *강제*하지 않음.
  3. **retrieval 연계 부족**: figure chunk가 top-5 filler 자리에 들어갈 뿐, 해당 parent가 인용되지 않기 때문에 LLM이 figure 맥락을 답변에 엮을 동기가 없음.

### 5.2 Vision ON이 multi-source 다양성을 오히려 낮춘다

- Distinct cited parent: ON=2.17, OFF=3.17 → **−1.00**
- 6/6 케이스에서 OFF가 같거나 더 많이 인용
- 메커니즘 가설: 이미지 토큰이 attention을 할당받으면서 텍스트 근거를 크로스-레퍼런스하는 여력이 줄어듦. 결과적으로 답변이 더 짧고(−27%) cite가 줄어듦.

### 5.3 Numeric-value verbatim 인용은 ON이 소폭 유리

- ON=0.83, OFF=0.17 → +0.67  
- 단 **대부분 0/0**이라 표본이 매우 얕음(케이스 2개에서만 유의미한 count). "vision이 수치 인용을 돕는다"고 결론 내리기 어려움.

### 5.4 페어 유사도가 stochastic baseline과 동급

- 페어 평균 Jaccard = 0.022, 케이스간 평균 = 0.024 → **거의 같음**
- 즉 vision 조건이 만드는 답변 차이와, LLM을 두 번 다른 시드로 돌렸을 때의 차이가 구분되지 않음

---

## 6. 한계

1. **표본 N=6**: 통계적 검정력 부족. 개별 Δ는 케이스별 변동 폭보다 작음.
2. **단일 논문 코퍼스**: figure 1장. vision 잠재 효용을 평가하기에 근본적으로 부적합한 테스트 환경.
3. **LLM temperature 기본값**: 재현마다 답변이 크게 달라지므로 paired 1회 비교로 인과 분석 어려움. Seed 고정 또는 N회 repeat 후 평균이 필요.
4. **OCR 품질**: figure chunk의 OCR 텍스트 품질을 별도로 확인하지 않음. 이미지가 텍스트와 중복 정보만 담고 있다면 vision의 marginal value가 0에 가까움.

---

## 7. 권고

1. **당분간 기본값 = `--vision` off 로 운용**  
   - 현 코퍼스·현 프롬프트에서 ON의 명확한 이득 없음, 오히려 cite/길이에서 약세
   - API 이미지 토큰 비용 절약

2. **Vision을 의미있게 평가하려면 아래 3가지가 선행되어야 함**  
   - (a) **코퍼스에 figure가 많은 논문 추가** (플롯, 유병률 그래프, 알고리즘 트리 등)
   - (b) **프롬프트에 figure 인용 강제 규칙 추가**: 예) "For any attached figure, reproduce its key axis labels or flow step in ≤1 sentence and cite the parent_block_id."
   - (c) **OCR vs image 불일치 케이스 설계**: 텍스트만 보면 틀리고, 이미지를 봐야 맞는 질문을 만들어 vision-only signal 측정

3. **보조 수정**
   - retrieval 단계에서 figure chunk를 강조하거나, figure가 포함된 parent를 top-5 내에 조기 삽입하는 mild boost 검토
   - p3/p8/p10 같은 새 "never-cited filler"를 2차 필터 대상으로 검토 (vision 이슈와는 별개)

4. **문서화**  
   - `README.md`에 "vision 기본값: OFF, 코퍼스 확장 시 재평가" 원칙 반영
   - 이 리포트를 `reports/`에 남겨 이후 코퍼스 확장 후 delta 측정의 기준선으로 사용

---

## 8. 재현 방법

```bash
# 공통 환경 준비
cd /gpfs/data/razavianlab/capstone/2025_rag/agentic_rag_kk5739
module load python/gpu/3.10.6
export LD_LIBRARY_PATH=/gpfs/share/apps/python/gpu/3.10.6/lib:${LD_LIBRARY_PATH:-}

# Vision ON (이미 outputs/CASE_XX.md 로 존재)
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

집계 스크립트(메트릭 계산)는 이 리포트 생성에 사용된 ad-hoc 스크립트이며, 필요 시 `scripts/` 하위로 정식화 예정.
