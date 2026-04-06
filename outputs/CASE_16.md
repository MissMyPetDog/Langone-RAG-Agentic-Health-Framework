# Question

For a 64-year-old male with acute kidney injury (AKI) onset shortly after ICU admission, how should treatment be optimized considering comorbidities including congestive heart failure, COPD, and malignancy, alongside current use of an ACEI/ARB, diuretic, and antibiotic, with historical NSAID use potentially impacting renal function and fluid balance, all within the context of elevated BMI and hypertension?

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=False, topn=5

**Vision:** 6 figure(s) sent as `image_url` (pixels). max=6 | VISION_MAX_EDGE=1536

---

## Answer

### Summary

For a 64-year-old male with acute kidney injury (AKI), comorbidities, and current medication use, optimizing treatment involves addressing nephrotoxicity, fluid balance, and monitoring kidney function. The patient’s acute setting further complicates management due to preexisting congestive heart failure (CHF), chronic obstructive pulmonary disease (COPD), and malignancy, combined with a history of NSAID use, hypertension, and elevated BMI.

### Options for Optimization

1. **Discontinue Nephrotoxic Agents**
   - **Appropriate**: Immediately stop any nephrotoxic medications to prevent worsening renal function. For this patient, consider discontinuing NSAIDs and reviewing ACEI/ARB usage in the context of hypotension or worsening renal function [Figure 4, pmid_23499048_p12].
   - **Avoid**: If discontinuation leads to uncontrolled hypertension or cardiac decompensation, continue with cautious monitoring.
   - **Support**: Recommendations emphasize halting nephrotoxic agents as a universal priority across all AKI stages [Figure 4, pmid_23499048_p12].

2. **Volume Status and Perfusion Pressure**
   - **Appropriate**: Ensure adequate intravascular volume and perfusion pressure, crucial for those with CHF. Avoid excessive fluid administration that may exacerbate heart failure; use diuretics only for volume overload [3.4.2, pmid_23499048_p12].
   - **Avoid**: Overusing diuretics in the absence of volume overload, as this might further impair renal perfusion.
   - **Support**: KDIGO guidelines emphasize volume management and avoiding diuretics outside volume overload cases [3.4.2, pmid_23499048_p12].

3. **Functional Hemodynamic Monitoring**
   - **Appropriate**: Utilize functional hemodynamic monitoring to optimize resuscitation efforts, particularly important for managing CHF and potential septic shock, which align with this patient’s ICU setting [3.1.3, pmid_23499048_p12].
   - **Avoid**: Minimizing monitoring in rapidly changing settings, which could lead to mismanagement of fluid status or perfusion goals.
   - **Support**: Protocol-based management to prevent AKI progression in critical conditions like CHF [3.1.3, pmid_23499048_p12].

### Conclusion

Each treatment approach aligns with KDIGO recommendations to prioritize non-nephrotoxic interventions, careful volume management, and comprehensive monitoring in acute settings. Adjustments are required if contraindications such as hypertension control failure or worsening CHF symptoms arise. Continuous monitoring and adjustment are essential given the complex clinical picture.

### References

- KDIGO guidelines for volume and perfusion management [3.1.3, 3.4.2, pmid_23499048].
- KDIGO recommendations on nephrotoxic agent discontinuation [Figure 4, pmid_23499048_p12].
- Supportive care recommendations in AKI [3.1.3, 3.4.2, pmid_23499048_p12].

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

### === DOC pmid_23499048 / KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury. / pmid_23499048_p12 ===

**`pmid_23499048_p12_fig_0_c0`** *(image)*

![page_12_fig_0.png](../data/raw/pmid_23499048/page_12_fig_0.png)

**OCR text**

```
AKIStage HighRisk 2 3 Discontinue all nephrotoxic agents when possible Ensurevolumestatus and perfusionpressure Consider functional hemodynamicmonitoring Monitor Serum creatinine and urine output Avoid hyperglycemia Consideralternativestoradiocontrastprocedures Non-invasivediagnosticworkup Considerinvasive diagnosticworkup Checkforchanges in drug dosing Consider Renal Replacement Therapy ConsiderICuadmission Avoid subclavian catheters ifpossible
```

**`pmid_23499048_p12_t0_c0`** *(text)*

3.1.3: We suggest using protocol-based management of hemodynamic and oxygenation parameters to prevent development or worsening of AKI in high-risk patients in the perioperative setting (2C) or in patients with septic shock (2C). 3.3.1: In critically ill patients, we suggest insulin therapy targeting plasma glucose 110–149 mg/dl (6.1–8.3mmol/l). (2C) 3.3.2: We suggest achieving a total energy intake of 20–30 kcal/kg/d in patients with any stage of AKI. (2C) 3.3.3: We suggest to avoid restriction of protein intake with the aim of preventing or delaying initiation of RRT. (2D) 3.3.4: We suggest administering 0.8–1.0 g/kg/d of protein in noncatabolic AKI patients without need for dialysis (2D), 1.0–1.5 g/kg/d in patients with AKI on RRT (2D), and up to a maximum of 1.7 g/kg/d in patients on continuous renal replacement therapy (CRRT) and in hypercatabolic patients. (2D) 3.3.5: We suggest providing nutrition preferentially via the enteral route in patients with AKI. (2C) 3.4.1: We recommend not using diuretics to prevent AKI. (1B) 3.4.2: We suggest not using diuretics to treat AKI, except in the management of volume overload. (2C) 3.5.1: We recommend not using low-dose dopamine to prevent or treat AKI.

**`pmid_23499048_p12_t1_c0`** *(text)*

1: We suggest that a single dose of theophylline may be given in neonates with severe perinatal asphyxia, who are at high risk of AKI. (2B) 3.8.1: We suggest not using aminoglycosides for the treatment of infections unless no suitable, less nephrotoxic, therapeutic alternatives are available. (2A) 3.8.2: We suggest that, in patients with normal kidney function in steady state, aminoglycosides are administered as a single dose daily rather than multiple-dose daily treatment regimens. (2B) 3.8.3: We recommend monitoring aminoglycoside drug levels when treatment with multiple daily dosing is used for more than 24 hours. (1A) 3.8.4: We suggest monitoring aminoglycoside drug levels when treatment with single-daily dosing is used for more than 48 hours. (2C) 3.8.5: We suggest using topical or local applications of aminoglycosides (e.g., respiratory aerosols, instilled antibiotic beads), rather than i.v. application, when feasible and suitable. (2B) 3.8.6: We suggest using lipid formulations of amphotericin B rather than conventional formulations of amphotericin B. (2A) 3.8.7: In the treatment of systemic mycoses or parasitic infections, we recommend using azole antifungal agents and/or the echinocandins rather than conventional amphotericin B, if equal therapeutic efﬁcacy can be assumed.

**`pmid_23499048_p12_t2_c0`** *(text)*

Kidney International Supplements (2012) 2, 8–12 9 summary of recommendation statements

**`pmid_23499048_p12_t0_c1`** *(text)*

(2D) 3.3.5: We suggest providing nutrition preferentially via the enteral route in patients with AKI. (2C) 3.4.1: We recommend not using diuretics to prevent AKI. (1B) 3.4.2: We suggest not using diuretics to treat AKI, except in the management of volume overload. (2C) 3.5.1: We recommend not using low-dose dopamine to prevent or treat AKI. (1A) 3.5.2: We suggest not using fenoldopam to prevent or treat AKI. (2C) 3.5.3: We suggest not using atrial natriuretic peptide (ANP) to prevent (2C) or treat (2B) AKI. 3.6.1: We recommend not using recombinant human (rh)IGF-1 to prevent or treat AKI. (1B) 3.7.

**`pmid_23499048_p12_t1_c1`** *(text)*

(2B) 3.8.6: We suggest using lipid formulations of amphotericin B rather than conventional formulations of amphotericin B. (2A) 3.8.7: In the treatment of systemic mycoses or parasitic infections, we recommend using azole antifungal agents and/or the echinocandins rather than conventional amphotericin B, if equal therapeutic efﬁcacy can be assumed. (1A) Figure 4 | Stage-based management of AKI. Shading of boxes indicates priority of action—solid shading indicates actions that are equally appropriate at all stages whereas graded shading indicates increasing priority as intensity increases. AKI, acute kidney injury; ICU, intensive- care unit.

**`pmid_23499048_p12_t0_c2`** *(text)*

(2C) 3.5.1: We recommend not using low-dose dopamine to prevent or treat AKI. (1A) 3.5.2: We suggest not using fenoldopam to prevent or treat AKI. (2C) 3.5.3: We suggest not using atrial natriuretic peptide (ANP) to prevent (2C) or treat (2B) AKI. 3.6.1: We recommend not using recombinant human (rh)IGF-1 to prevent or treat AKI. (1B) 3.7.

**`pmid_23499048_p12_t1_c2`** *(text)*

(1A) Figure 4 | Stage-based management of AKI. Shading of boxes indicates priority of action—solid shading indicates actions that are equally appropriate at all stages whereas graded shading indicates increasing priority as intensity increases. AKI, acute kidney injury; ICU, intensive- care unit.

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

