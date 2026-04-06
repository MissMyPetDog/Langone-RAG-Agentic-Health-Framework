# Question

What are the most effective and safe treatment options for an 84-year-old male patient with acute kidney injury (creatinine increased to 2.10 mg/dL from baseline 1.50 mg/dL) and low bicarbonate levels (9.0 mEq/L), considering his history of myocardial infarction, congestive heart failure, severe liver disease, current use of nephrotoxic agent, antibiotic, and anticoagulant medications, while accounting for potential contraindications and comorbid conditions?

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=False, topn=5

**Vision:** 6 figure(s) sent as `image_url` (pixels). max=6 | VISION_MAX_EDGE=1536

---

## Answer

**Summary:**
For an 84-year-old male with acute kidney injury (AKI), low bicarbonate levels, previous myocardial infarction, congestive heart failure, severe liver disease, and the use of nephrotoxic agents, careful selection of treatment is necessary to avoid exacerbating his conditions. The context suggests potential interventions and their implications based on available data.

**Treatment Options:**

1. **Sodium Bicarbonate Infusion:**
   - **Appropriate:** Sodium bicarbonate may be beneficial in managing metabolic acidosis (evidenced by low bicarbonate levels) and may help prevent contrast-induced acute kidney injury (CI-AKI) [KDOQI US commentary (pmid_23499048_p85)].
   - **Avoid if:** Preparation errors could result in hypertonic solutions – crucial to ensure correct preparation [KDOQI US commentary (pmid_23499048_p85)].
   - **Considerations:** Monitor closely for fluid overload due to his congestive heart failure. Control the infusion rate to minimize cardiovascular strain.

2. **Isotonic Saline Infusion:**
   - **Appropriate:** Isotonic saline is a standard treatment for fluid and electrolyte balance in AKI prevention. It is less error-prone than sodium bicarbonate [KDOQI US commentary (pmid_23499048_p85)].
   - **Avoid if:** The patient has severe fluid overload or uncontrolled heart failure, as isotonic saline may exacerbate these conditions.
   - **Considerations:** Saline may be considered if concerns about bicarbonate administration errors are high or if the patient shows signs of volume depletion.

3. **N-acetylcysteine (NAC):**
   - **Appropriate:** Administer in conjunction with either sodium bicarbonate or isotonic saline for preventing CI-AKI, leveraging its antioxidative properties [KDOQI US commentary (pmid_23499048_p85)].
   - **Avoid if:** The patient has a known allergy to NAC or if there are severe pulmonary issues, as NAC can sometimes exacerbate these [KDOQI US commentary (pmid_23499048_p85)].
   - **Considerations:** Ensure appropriate dosing alongside bicarbonate or saline to maximize the protective effect on renal function.

**Fallback Logic:**

- Begin with sodium bicarbonate if metabolic acidosis is pronounced and conditions allow for meticulous preparation to avoid dilution errors.
- Move to isotonic saline if bicarbonate preparation risks are prohibitive, ensuring fluid balance is closely monitored.
- Couple NAC with either option to enhance renal protective effects if no contraindications exist.

**References:**

- **pmid_23499048_p85**: Provides insights into the effectiveness of sodium bicarbonate over normal saline in CI-AKI and discusses potential issues related to bicarbonate administration.
- **pmid_23499048_p2, pmid_23499048_p3**: Outline guidelines on the treatment and prevention strategies for AKI.

Please consult a healthcare provider for personalized medical advice.

---

## Used Sources (with context)

### === DOC pmid_23499048 / KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury. / pmid_23499048_p1 ===

**`pmid_23499048_p1_fig_0_c0`** *(image)*

![page_1_fig_0.png](../data/raw/pmid_23499048/page_1_fig_0.png)

**OCR text**

```
KIDNEY DIGO R GLOBAL
```

**`pmid_23499048_p1_fig_1_c0`** *(image)*

![page_1_fig_1.png](../data/raw/pmid_23499048/page_1_fig_1.png)

**`pmid_23499048_p1_fig_2_c0`** *(image)*

![page_1_fig_2.png](../data/raw/pmid_23499048/page_1_fig_2.png)

**`pmid_23499048_p1_fig_3_c0`** *(image)*

![page_1_fig_3.png](../data/raw/pmid_23499048/page_1_fig_3.png)

**`pmid_23499048_p1_fig_4_c0`** *(image)*

![page_1_fig_4.png](../data/raw/pmid_23499048/page_1_fig_4.png)

**`pmid_23499048_p1_fig_5_c0`** *(image)*

![page_1_fig_5.png](../data/raw/pmid_23499048/page_1_fig_5.png)

**`pmid_23499048_p1_fig_6_c0`** *(image)*

![page_1_fig_6.png](../data/raw/pmid_23499048/page_1_fig_6.png)

**`pmid_23499048_p1_fig_7_c0`** *(image)*

![page_1_fig_7.png](../data/raw/pmid_23499048/page_1_fig_7.png)

**`pmid_23499048_p1_fig_8_c0`** *(image)*

![page_1_fig_8.png](../data/raw/pmid_23499048/page_1_fig_8.png)

**`pmid_23499048_p1_t0_c0`** *(text)*

VOLUME 2 | ISSUE 1 | MARCH 2012 http://www.kidney-international.org OFFICIAL JOURNAL OF THE INTERNATIONAL SOCIETY OF NEPHROLOGY KDIGO Clinical Practice Guideline for Acute Kidney Injury

### === DOC pmid_23499048 / KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury. / pmid_23499048_p2 ===

**`pmid_23499048_p2_fig_0_c0`** *(image)*

![page_2_fig_0.png](../data/raw/pmid_23499048/page_2_fig_0.png)

**OCR text**

```
DISEASE KIDNEY GLOBAL
```

**`pmid_23499048_p2_t0_c0`** *(text)*

KDIGO Clinical Practice Guideline for Acute Kidney Injury Tables and Figures iv Notice 1 Work Group Membership 2 KDIGO Board Members 3 Reference Keys 4 Abbreviations and Acronyms 5 Abstract 6 Foreword 7 Summary of Recommendation Statements 8 Section 1: Introduction and Methodology 13 Chapter 1.1: Introduction 13 Chapter 1.2: Methodology 17 Section 2: AKI Definition 19 Chapter 2.1: Definition and classification of AKI 19 Chapter 2.2: Risk assessment 23 Chapter 2.3: Evaluation and general management of patients with and at risk for AKI 25 Chapter 2.4: Clinical applications 28 Chapter 2.5: Diagnostic approach to alterations in kidney function and structure 33 Section 3: Prevention and Treatment of AKI 37 Chapter 3.1: Hemodynamic monitoring and support for prevention and management of AKI 37 Chapter 3.2: General supportive management of patients with AKI, including management of complications 42 Chapter 3.3: Glycemic control and nutritional support 43 Chapter 3.4: The use of diuretics in AKI 47 Chapter 3.5: Vasodilator therapy: dopamine, fenoldopam, and natriuretic peptides 50 Chapter 3.6: Growth factor intervention 57 Chapter 3.7: Adenosine receptor antagonists 59 Chapter 3.8: Prevention of aminoglycoside- and amphotericin-related AKI 61 Chapter 3.9: Other methods of prevention of AKI in the critically ill 66 Section 4: Contrast-induced AKI 69 Chapter 4.1: Contrast-induced AKI: definition, epidemiology, and prognosis 69 Chapter 4.2: Assessment of the population at risk for CI-AKI 72 Chapter 4.3: Nonpharmacological prevention strategies of CI-AKI 76 Chapter 4.

**`pmid_23499048_p2_t1_c0`** *(text)*

4: Pharmacological prevention strategies of CI-AKI 80 Chapter 4.5: Effects of hemodialysis or hemofiltration 87 Section 5: Dialysis Interventions for Treatment of AKI 89 Chapter 5.1: Timing of renal replacement therapy in AKI 89 Chapter 5.2: Criteria for stopping renal replacement therapy in AKI 93 Chapter 5.3: Anticoagulation 95 Chapter 5.4: Vascular access for renal replacement therapy in AKI 101 Chapter 5.5: Dialyzer membranes for renal replacement therapy in AKI 105 Chapter 5.6: Modality of renal replacement therapy for patients with AKI 107 Chapter 5.7: Buffer solutions for renal replacement therapy in patients with AKI 111 Chapter 5.8: Dose of renal replacement therapy in AKI 113 Biographic and Disclosure Information 116 Acknowledgments 122 References 124 http://www.kidney-international.

**`pmid_23499048_p2_t2_c0`** *(text)*

org contents & 2012 KDIGO VOL 2 | SUPPLEMENT 1 | MARCH 2012

### === DOC pmid_23499048 / KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury. / pmid_23499048_p3 ===

**`pmid_23499048_p3_t0_c0`** *(text)*

TABLES Table 1. Implications of the strength of a recommendation 18 Table 2. Staging of AKI 19 Table 3. Comparison of RIFLE and AKIN criteria for diagnosis and classification of AKI 21 Table 4. Cross-tabulation of patients classified by RIFLE vs. AKIN 21 Table 5. Causes of AKI and diagnostic tests 22 Table 6. Causes of AKI: exposures and susceptibilities for non-specific AKI 23 Table 7. AKI diagnosis 28 Table 8. Overview of the approaches to determine baseline SCr in the application of RIFLE classification in previous studies 29 Table 9. Estimated baseline SCr 29 Table 10. AKI staging 30 Table 11. Definitions of AKI, CKD, and AKD 33 Table 12. Examples of AKI, CKD, and AKD based on GFR and increases in SCr 33 Table 13. Markers of kidney damage in AKD and CKD 35 Table 14. Integrated approach to interpret measures of kidney function and structure for diagnosis of AKI, AKD, and CKD 35 Table 15. CI-AKI risk-scoring model for percutaneous coronary intervention 73 Table 16. Additional radiological measures to reduce CI-AKI 77 Table 17. Potential applications for RRT 91 Table 18. Fluid overload and outcome in critically ill children with AKI 91 Table 19. Overview of the advantages and disadvantages of different anticoagulants in AKI patients 97 Table 20.

**`pmid_23499048_p3_t1_c0`** *(text)*

The RIFLE criteria for AKI 14 Figure 2. Overview of AKI, CKD, and AKD 20 Figure 3. Conceptual model for AKI 20 Figure 4. Stage-based management of AKI 25 Figure 5. Evaluation of AKI according to the stage and cause 26 Figure 6. Chronic Kidney Disease Epidemiology Collaboration cohort changes in eGFR and final eGFR corresponding to KDIGO definition and stages of AKI 34 Figure 7. GFR/SCr algorithm 34 Figure 8. Conceptual model for development and clinical course of AKI 38 Figure 9. Effect of furosemide vs. control on all-cause mortality 48 Figure 10. Effect of furosemide vs. control on need for RRT 48 Figure 11. Effect of low-dose dopamine on mortality 51 Figure 12. Effect of low-dose dopamine on need for RRT 52 Figure 13. Sample questionnaire 73 Figure 14. Risk for contrast-induced nephropathy 78 Figure 15. Bicarbonate vs. saline and risk of CI-AKI 81 Figure 16. NAC and bicarbonate vs. NAC for risk of CI-AKI 85 Figure 17. Flow-chart summary of recommendations 96 Additional information in the form of supplementary materials can be found online at http://www.kdigo.org/clinical_practice_guidelines/AKI.php contents http://www.kidney-international.

**`pmid_23499048_p3_t2_c0`** *(text)*

org & 2012 KDIGO iv Kidney International Supplements (2012) 2, iv

**`pmid_23499048_p3_t0_c1`** *(text)*

Additional radiological measures to reduce CI-AKI 77 Table 17. Potential applications for RRT 91 Table 18. Fluid overload and outcome in critically ill children with AKI 91 Table 19. Overview of the advantages and disadvantages of different anticoagulants in AKI patients 97 Table 20. Catheter and patient sizes 104 Table 21. Typical setting of different RRT modalities for AKI (for 70-kg patient) 107 Table 22. Theoretical advantages and disadvantages of CRRT, IHD, SLED, and PD 108 Table 23. Microbiological quality standards of different regulatory agencies 112 FIGURES Figure 1.

**`pmid_23499048_p3_t1_c1`** *(text)*

NAC for risk of CI-AKI 85 Figure 17. Flow-chart summary of recommendations 96 Additional information in the form of supplementary materials can be found online at http://www.kdigo.org/clinical_practice_guidelines/AKI.php contents http://www.kidney-international.

**`pmid_23499048_p3_t0_c2`** *(text)*

Catheter and patient sizes 104 Table 21. Typical setting of different RRT modalities for AKI (for 70-kg patient) 107 Table 22. Theoretical advantages and disadvantages of CRRT, IHD, SLED, and PD 108 Table 23. Microbiological quality standards of different regulatory agencies 112 FIGURES Figure 1.

### === DOC pmid_23499048 / KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury. / pmid_23499048_p85 ===

**`pmid_23499048_p85_t0_c0`** *(text)*

developed in 1.7% in the bicarbonate group, compared to 13.6% in the saline solution group. Ozcan et al.483 included three prophylactic regimens: infusion of sodium bicarbonate, sodium chloride, and sodium chloride plus oral NAC (600 mg b.i.d.). The incidence of CI-AKI, deﬁned as an increase in SCr level 425% or 0.5 mg/dl (44.2 mmol/l) after 48 hours was signiﬁcantly lower in the sodium bicarbonate group (4.5%) compared to sodium chloride alone (13.6%, P ¼ 0.036). After adjusting for the Mehran nephropathy risk score, the risk of CI-AKI signiﬁ- cantly reduced with sodium bicarbonate compared to sodium chloride alone (adjusted risk ratio 0.29; P ¼ 0.043). By contrast, Adolph et al.482 did not ﬁnd differences in CI- AKI between the two ﬂuid regimens on day 1 after angiography; even on day 2, most parameters were similar in both groups. In none of the above-mentioned studies was there need for RRT. Finally, a recent but retrospective study485 deﬁned CI-AKI as an increase in SCr X25% within 48 hours of receiving contrast media, and compared sodium bicarbonate to normal saline in patients exposed to cardiac angiography. One group of patients (n ¼ 89) received prophylactic bicarbonate; a second group, normal saline (n ¼ 98).

**`pmid_23499048_p85_t1_c0`** *(text)*

3%) in the normal saline group and no signiﬁcant change in the bicarbonate group. Three patients (3.4%) in the bicarbonate group, as opposed to 14 patients (14.3%) in the normal saline group, developed CI-AKI (P ¼ 0.011). Two patients in the normal saline group and none in the bicarbonate group needed dialysis. This study suggests that the use of i.v. sodium bicarbonate is more effective than normal saline in preventing CI-AKI. Three studies compared bicarbonate and saline solutions associated with the administration of NAC in both study arms.486–488 Recio-Mayoral et al.488 conducted a prospective single-center RCT in 111 consecutive patients with acute coronary syndrome undergoing emergency angioplasty. One group of patients received an infusion of sodium bicarbonate plus NAC started just before contrast-media injection and continued for 12 hours after angioplasty. The second (control) group received the standard ﬂuid protocol consist- ing of i.v. isotonic saline for 12 hours after angioplasty. In both groups, two doses of oral NAC were administered the next day. A SCr concentration 40.5 mg/dl (444.2 mmol/l) from baseline after emergency angioplasty was observed in 1.8% in the bicarbonate group and in 21.8% of the saline group.

**`pmid_23499048_p85_t2_c0`** *(text)*

9% saline infusion plus NAC (n ¼ 111), sodium bicarbonate infusion plus NAC (n ¼ 108), and 0.9% saline plus ascorbic acid plus NAC (n ¼ 107). CI-AKI was deﬁned as an increase of X25% in the SCr concentration 48 hours after the procedure. CI-AKI occurred in 9.9% of the saline plus NAC group, in 1.9% of the bicarbonate/NAC group (P ¼ 0.019 vs. saline plus NAC group), and in 10.3% of the saline plus ascorbic acid plus NAC group (P ¼ 1.00 vs. saline plus NAC group). There was no difference in mortality nor in need for RRT among the different groups. While these two studies suggest that isotonic bicarbonate may provide greater beneﬁt than isotonic saline, either in association with NAC or not, neither study can be considered conclusive. Maioli et al.487 prospectively compared the efﬁcacy of sodium bicarbonate vs. isotonic saline in addition to NAC in a larger population of 502 patients with an estimated CrCl o60 ml/min, and undergoing coronary angiography or intervention. CI-AKI was deﬁned as an absolute increase of SCr X0.5 mg/dl (X44.2 mmol/l) measured within 5 days. CI- AKI occurred in 10.8%; 10% were treated with sodium bicarbonate and 11.5% with saline. In patients with CI-AKI, the mean increase in creatinine was not signiﬁcantly different in the two study groups.

**`pmid_23499048_p85_t3_c0`** *(text)*

sodium bicarbonate was associated with an increased incidence of CI-AKI.489 While one might take the position that, if in doubt, one should choose the regimen that is potentially superior, the Work Group also considered the potential harm. In addition, isotonic bicarbonate solutions are usually composed by adding 154 ml of 8.4% sodium bicarbonate (i.e., 1 mmol/ ml) to 846 ml of 5% glucose solution, resulting in a ﬁnal sodium and bicarbonate concentration of 154 mmol/l each. Since this mixing of the solution is often done at the bedside or in the hospital pharmacy, there is the possibility for errors leading to the infusion of a hypertonic bicarbonate solution. The potential for harm from dosing errors, and the added burden from preparation of the bicarbonate solution, has to be taken into account in clinical practice when making a choice between using bicarbonate rather than standard isotonic saline solutions. Taken together, the Work Group concluded that there is a possible but inconsistent beneﬁt of bicarbonate solutions based on overall moderate-quality evidence (Suppl Table 22). As discussed above, the potential of harm and the additional burden for preparing the bicarbonate solutions led the Work Group not to express a preference for or against one solution (isotonic saline or isotonic bicarbonate).

**`pmid_23499048_p85_t4_c0`** *(text)*

4

**`pmid_23499048_p85_t0_c1`** *(text)*

In none of the above-mentioned studies was there need for RRT. Finally, a recent but retrospective study485 deﬁned CI-AKI as an increase in SCr X25% within 48 hours of receiving contrast media, and compared sodium bicarbonate to normal saline in patients exposed to cardiac angiography. One group of patients (n ¼ 89) received prophylactic bicarbonate; a second group, normal saline (n ¼ 98). The patients in the bicarbonate group had more severe renal disease with higher baseline SCr (1.58 ± 0.5 mg/dl; 140 ± 44.2 mmol/l) vs. (1.28 ± 0.3 mg/dl; 113 ± 26.5 mmol/l), P ¼ 0.001 and a lower eGFR, compared to the normal saline group. After contrast-media exposure, there was signiﬁcant drop in eGFR (6.4%) and increase in SCr (11.

**`pmid_23499048_p85_t1_c1`** *(text)*

isotonic saline for 12 hours after angioplasty. In both groups, two doses of oral NAC were administered the next day. A SCr concentration 40.5 mg/dl (444.2 mmol/l) from baseline after emergency angioplasty was observed in 1.8% in the bicarbonate group and in 21.8% of the saline group. Mortality and need for RRT were not signiﬁcantly different between both groups. Briguori et al.486 randomized 326 CKD patients (SCr X2 mg/dl [X177 mmol/l] and/or eGFR o40 ml/min per 1.73 m2), and referred for coronary and/or peripheral procedures to three different protocols: prophylactic administration of 0.

**`pmid_23499048_p85_t2_c1`** *(text)*

CI-AKI was deﬁned as an absolute increase of SCr X0.5 mg/dl (X44.2 mmol/l) measured within 5 days. CI- AKI occurred in 10.8%; 10% were treated with sodium bicarbonate and 11.5% with saline. In patients with CI-AKI, the mean increase in creatinine was not signiﬁcantly different in the two study groups. Based on this last prospective study, bicarbonate does not seem to be more efﬁcient than saline. Furthermore, a retrospective cohort study at the Mayo Clinic assessed the risk of CI-AKI associated with the use of sodium bicarbonate, NAC, or the combination. Surprisingly, i.v.

**`pmid_23499048_p85_t3_c1`** *(text)*

Taken together, the Work Group concluded that there is a possible but inconsistent beneﬁt of bicarbonate solutions based on overall moderate-quality evidence (Suppl Table 22). As discussed above, the potential of harm and the additional burden for preparing the bicarbonate solutions led the Work Group not to express a preference for or against one solution (isotonic saline or isotonic bicarbonate). Thus, either can be used for the prevention of CI-AKI. 4.4.2: We recommend not using oral ﬂuids alone in patients at increased risk of CI-AKI. (1C) 82 Kidney International Supplements (2012) 2, 69–88 chapter 4.

**`pmid_23499048_p85_t0_c2`** *(text)*

The patients in the bicarbonate group had more severe renal disease with higher baseline SCr (1.58 ± 0.5 mg/dl; 140 ± 44.2 mmol/l) vs. (1.28 ± 0.3 mg/dl; 113 ± 26.5 mmol/l), P ¼ 0.001 and a lower eGFR, compared to the normal saline group. After contrast-media exposure, there was signiﬁcant drop in eGFR (6.4%) and increase in SCr (11.

**`pmid_23499048_p85_t1_c2`** *(text)*

Mortality and need for RRT were not signiﬁcantly different between both groups. Briguori et al.486 randomized 326 CKD patients (SCr X2 mg/dl [X177 mmol/l] and/or eGFR o40 ml/min per 1.73 m2), and referred for coronary and/or peripheral procedures to three different protocols: prophylactic administration of 0.

**`pmid_23499048_p85_t2_c2`** *(text)*

In patients with CI-AKI, the mean increase in creatinine was not signiﬁcantly different in the two study groups. Based on this last prospective study, bicarbonate does not seem to be more efﬁcient than saline. Furthermore, a retrospective cohort study at the Mayo Clinic assessed the risk of CI-AKI associated with the use of sodium bicarbonate, NAC, or the combination. Surprisingly, i.v.

**`pmid_23499048_p85_t3_c2`** *(text)*

As discussed above, the potential of harm and the additional burden for preparing the bicarbonate solutions led the Work Group not to express a preference for or against one solution (isotonic saline or isotonic bicarbonate). Thus, either can be used for the prevention of CI-AKI. 4.4.2: We recommend not using oral ﬂuids alone in patients at increased risk of CI-AKI. (1C) 82 Kidney International Supplements (2012) 2, 69–88 chapter 4.

