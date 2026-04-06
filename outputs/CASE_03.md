# Question

In a 50-year-old male with acute kidney injury (baseline creatinine 0.80 mg/dL to 1.70 mg/dL within 12.8 hours of ICU admission) on anticoagulant treatment and a Charlson score of 16, how should management be adjusted considering comorbidities such as moderate/severe renal disease, severe liver disease, malignancy, cardiovascular conditions, chronic obstructive pulmonary disease, and a history of ACEI/ARB, diuretic, NSAID, and vancomycin use?

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=False, topn=5

**Vision:** 6 figure(s) sent as `image_url` (pixels). max=6 | VISION_MAX_EDGE=1536

---

## Answer

### Problem Summary

A 50-year-old male with acute kidney injury (AKI) has seen a significant rise in creatinine levels shortly after ICU admission. He is on anticoagulant therapy and has severe comorbidities, including moderate to severe renal disease, severe liver disease, malignancy, cardiovascular conditions, COPD, and a history of using ACEI/ARB, diuretics, NSAIDs, and vancomycin. Management in this context should carefully consider the patient's risk factors for bleeding and drug interactions.

### Evidence and Discussion

The management of AKI in critically ill patients, especially those on anticoagulant therapy, must balance maintaining renal function and managing the risk of bleeding [KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury (pmid_23499048)].

1. **Use of Regional Citrate Anticoagulation:**
   - Regional citrate anticoagulation is preferred over systemic heparin anticoagulation in critically ill patients with AKI undergoing continuous renal replacement therapy (CRRT) [Monchi et al. (KDOQI, pmid_23499048)]. Citrate reduces bleeding risks compared to heparin, making it suitable for patients with high comorbidity scores, like the one described.
   - **Appropriate When:** High risk of bleeding is present, such as in this patient with multiple comorbidities and concurrent anticoagulant therapy.
   - **Avoid When:** Severe liver dysfunction, as citrate metabolism may be impaired, leading to accumulation and potential toxicity.
   - **Supporting Evidence:** [Monchi et al. (pmid_23499048_p2)], [Hetzel et al. and Kramer et al. for metabolism concerns (pmid_23499048)].

2. **Low Molecular Weight Heparins (LMWH):**
   - LMWHs may be safer than unfractionated heparin due to lower risk of heparin-induced thrombocytopenia and easier monitoring [Gray E, et al. (pmid_23499048)].
   - **Appropriate When:** Patients have relatively preserved renal function or are at lower risk of citrate-related complications.
   - **Avoid When:** There is severe renal impairment or active bleeding risk.
   - **Supporting Evidence:** [Hirsh J et al., and Lim W et al. (pmid_23499048)].

3. **Unfractionated Heparin:**
   - Use of unfractionated heparin could be considered if neither citrate nor LMWH is feasible. It has a shorter half-life and is reversible.
   - **Appropriate When:** Rapid reversibility is required due to potential bleeding risks.
   - **Avoid When:** There is a high risk of heparin-induced thrombocytopenia or insufficient monitoring resources.
   - **Supporting Evidence:** [Fischer KG. (pmid_23499048)], [Warkentin TE, et al. for HIT risk (pmid_23499048)].

### Conclusion

Considering the presented patient's complex clinical status, regional citrate anticoagulation is the most preferred option, given its lower bleeding risk. If citrate is contraindicated due to liver dysfunction, LMWHs may be used cautiously. Unfractionated heparin remains an alternative when rapid reversibility is critical.

### References

- **Monchi M, Betjes MG.** Regional citrate versus heparin for anticoagulation (pmid_23499048_p2).
- **Gray E, Lim W, Hirsh J.** Safety and efficacy of low molecular weight heparins (pmid_23499048).
- **Fischer KG, Warkentin TE.** Anticoagulation essentials and HIT risk (pmid_23499048).

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

### === DOC pmid_23499048 / KDOQI US commentary on the 2012 KDIGO clinical practice guideline for acute kidney injury. / pmid_23499048_p138 ===

**`pmid_23499048_p138_t0_c0`** *(text)*

578. Joannidis M, Oudemans-van Straaten HM. Clinical review: Patency of the circuit in continuous renal replacement therapy. Crit Care 2007; 11: 218. 579. Davenport A. Review article: Low-molecular-weight heparin as an alternative anticoagulant to unfractionated heparin for routine outpatient haemodialysis treatments. Nephrology (Carlton) 2009; 14: 455–461. 580. Hirsh J, Bauer KA, Donati MB, et al. Parenteral anticoagulants: American College of Chest Physicians Evidence-Based Clinical Practice Guidelines (8th Edition). Chest 2008; 133: 141S–159S. 581. Warkentin TE, Greinacher A, Koster A, et al. Treatment and prevention of heparin-induced thrombocytopenia: American College of Chest Physicians Evidence-Based Clinical Practice Guidelines (8th Edition). Chest 2008; 133: 340S–380S. 582. Baglin T, Barrowcliffe TW, Cohen A, et al. Guidelines on the use and monitoring of heparin. Br J Haematol 2006; 133: 19–34. 583. Gray E, Mulloy B, Barrowcliffe TW. Heparin and low-molecular-weight heparin. Thromb Haemost 2008; 99: 807–818. 584. Martel N, Lee J, Wells PS. Risk for heparin-induced thrombocytopenia with unfractionated and low-molecular-weight heparin thromboprophylaxis: a meta-analysis. Blood 2005; 106: 2710–2715.

**`pmid_23499048_p138_t1_c0`** *(text)*

Safety and efﬁcacy of low molecular weight heparins for hemodialysis in patients with end-stage renal failure: a meta-analysis of randomized trials. J Am Soc Nephrol 2004; 15: 3192–3206. 587. European Best Practice Guidelines for Haemodialysis (Part 1). V. Chronic intermittent haemodialysis and prevention of clotting in the extracorporal system. Nephrol Dial Transplant 2002; 17 (Suppl 7): 63–71. 588. Fischer KG. Essentials of anticoagulation in hemodialysis. Hemodial Int 2007; 11: 178–189. 589. Ouseph R, Ward RA. Anticoagulation for intermittent hemodialysis. Semin Dial 2000; 13: 181–187. 590. Lim W, Dentali F, Eikelboom JW, et al. Meta-analysis: low-molecular- weight heparin and bleeding in patients with severe renal insufﬁciency. Ann Intern Med 2006; 144: 673–684. 591. Akizawa T, Koshikawa S, Ota K, et al. Nafamostat mesilate: a regional anticoagulant for hemodialysis in patients at high risk for bleeding. Nephron 1993; 64: 376–381. 592. Matsuo T, Kario K, Nakao K, et al. Anticoagulation with nafamostat mesilate, a synthetic protease inhibitor, in hemodialysis patients with a bleeding risk. Haemostasis 1993; 23: 135–141. 593. Yang JW, Han BG, Kim BR, et al. Superior outcome of nafamostat mesilate as an anticoagulant in patients undergoing maintenance hemodialysis with intracerebral hemorrhage.

**`pmid_23499048_p138_t2_c0`** *(text)*

Gen Pharmacol 1995; 26: 1627–1632. 596. Okada H, Suzuki H, Deguchi N, et al. Agranulocytosis in a haemodialysed patient induced by a proteinase inhibitor, nafamostate mesilate. Nephrol Dial Transplant 1992; 7: 980. 597. Novacek G, Kapiotis S, Jilma B, et al. Enhanced blood coagulation and enhanced ﬁbrinolysis during hemodialysis with prostacyclin. Thromb Res 1997; 88: 283–290. 598. Swartz RD, Flamenbaum W, Dubrow A, et al. Epoprostenol (PGI2, prostacyclin) during high-risk hemodialysis: preventing further bleeding complications. J Clin Pharmacol 1988; 28: 818–825. 599. Monchi M, Berghmans D, Ledoux D, et al. Citrate vs. heparin for anticoagulation in continuous venovenous hemoﬁltration: a prospective randomized study. Intensive Care Med 2004; 30: 260–265. 600. Kutsogiannis DJ, Gibney RT, Stollery D, et al. Regional citrate versus systemic heparin anticoagulation for continuous renal replacement in critically ill patients. Kidney Int 2005; 67: 2361–2367. 601. Betjes MG, van Oosterom D, van Agteren M, et al. Regional citrate versus heparin anticoagulation during venovenous hemoﬁltration in patients at low risk for bleeding: similar hemoﬁlter survival but signiﬁcantly less bleeding. J Nephrol 2007; 20: 602–608.

**`pmid_23499048_p138_t3_c0`** *(text)*

Regional anticoagulation with citrate is superior to systemic anticoagulation with heparin in critically ill patients undergoing continuous venovenous hemodiaﬁltration. Korean J Intern Med 2011; 26: 68–75. 602. Fealy N, Baldwin I, Johnstone M, et al. A pilot randomized controlled crossover study comparing regional heparinization to regional citrate anticoagulation for continuous venovenous hemoﬁltration. Int J Artif Organs 2007; 30: 301–307. 603. Oudemans-van Straaten HM, Bosman RJ, Koopmans M, et al. Citrate anticoagulation for continuous venovenous hemoﬁltration. Crit Care Med 2009; 37: 545–552. 604. Mehta RL, McDonald BR, Aguilar MM, et al. Regional citrate anti- coagulation for continuous arteriovenous hemodialysis in critically ill patients. Kidney Int 1990; 38: 976–981. 605. Morgera S, Scholle C, Voss G, et al. Metabolic complications during regional citrate anticoagulation in continuous venovenous hemodialysis: single-center experience. Nephron Clin Pract 2004; 97: c131–136. 606. Thoenen M, Schmid ER, Binswanger U, et al. Regional citrate anti- coagulation using a citrate-based substitution solution for continuous venovenous hemoﬁltration in cardiac surgery patients. Wien Klin Wochenschr 2002; 114: 108–114.

**`pmid_23499048_p138_t4_c0`** *(text)*

Wien Klin Wochenschr 1997; 109: 123–127. 609. Durao MS, Monte JC, Batista MC, et al. The use of regional citrate anticoagulation for continuous venovenous hemodiaﬁltration in acute kidney injury. Crit Care Med 2008; 36: 3024–3029. 610. Kramer L, Bauer E, Joukhadar C, et al. Citrate pharmacokinetics and metabolism in cirrhotic and noncirrhotic critically ill patients. Crit Care Med 2003; 31: 2450–2455. 611. Hetzel GR, Taskaya G, Sucker C, et al. Citrate plasma levels in patients under regional anticoagulation in continuous venovenous hemoﬁltration. Am J Kidney Dis 2006; 48: 806–811. 612. Meier-Kriesche HU, Gitomer J, Finkel K, et al. Increased total to ionized calcium ratio during continuous venovenous hemodialysis with regional citrate anticoagulation. Crit Care Med 2001; 29: 748–752. 613. Bakker AJ, Boerma EC, Keidel H, et al. Detection of citrate overdose in critically ill patients on citrate-anticoagulated venovenous haemoﬁltration: use of ionised and total/ionised calcium. Clin Chem Lab Med 2006; 44: 962–966. 614. Davies HT, Leslie G, Pereira SM, et al. A randomized comparative crossover study to assess the affect on circuit life of varying pre-dilution volume associated with CVVH and CVVHDF.

**`pmid_23499048_p138_t5_c0`** *(text)*

unfractionated heparin for anticoagulation during continuous veno-venous hemoﬁltration: a randomized controlled crossover study. Intensive Care Med 2007; 33: 1571–1579. 617. Stefanidis I, Hagel J, Frank D, et al. Hemostatic alterations during continuous venovenous hemoﬁltration in acute renal failure. Clin Nephrol 1996; 46: 199–205. 618. van de Wetering J, Westendorp RG, van der Hoeven JG, et al. Heparin use in continuous renal replacement procedures: the struggle between ﬁlter coagulation and patient hemorrhage. J Am Soc Nephrol 1996; 7: 145–150. 619. Yang RL, Liu DW. [Clinical evaluation of hemoﬁltration without anti- coagulation in critically ill patients at high risk of bleeding]. Zhongguo Yi Xue Ke Xue Yuan Xue Bao 2007; 29: 651–655. 620. Reeves JH, Cumming AR, Gallagher L, et al. A controlled trial of low-molecular-weight heparin (dalteparin) versus unfractionated heparin as anticoagulant during continuous venovenous hemodialysis with ﬁltration. Crit Care Med 1999; 27: 2224–2228. 621. de Pont AC, Oudemans-van Straaten HM, Roozendaal KJ, et al. Nadroparin versus dalteparin anticoagulation in high-volume, continuous venovenous hemoﬁltration: a double-blind, randomized, crossover study.

**`pmid_23499048_p138_t6_c0`** *(text)*

Anticoagulation with prostaglandins and unfractionated heparin during continuous venovenous haemoﬁltration: a randomized controlled trial. Wien Klin Wochenschr 2002; 114: 96–101. 624. Fabbri LP, Nucera M, Al Malyan M, et al. Regional anticoagulation and antiaggregation for CVVH in critically ill patients: a prospective, randomized, controlled pilot study. Acta Anaesthesiol Scand 2010; 54: 92–97.

**`pmid_23499048_p138_t7_c0`** *(text)*

Kidney International Supplements (2012) 2, 124–138 135 references

**`pmid_23499048_p138_t0_c1`** *(text)*

Heparin and low-molecular-weight heparin. Thromb Haemost 2008; 99: 807–818. 584. Martel N, Lee J, Wells PS. Risk for heparin-induced thrombocytopenia with unfractionated and low-molecular-weight heparin thromboprophylaxis: a meta-analysis. Blood 2005; 106: 2710–2715. 585. Davenport A, Tolwani A. Citrate anticoagulation for continuous renal replacement therapy (CRRT) in patients with acute kidney injury admitted to the intensive care unit. NDT Plus 2009; 2: 439–447. 586. Lim W, Cook DJ, Crowther MA.

**`pmid_23499048_p138_t1_c1`** *(text)*

Anticoagulation with nafamostat mesilate, a synthetic protease inhibitor, in hemodialysis patients with a bleeding risk. Haemostasis 1993; 23: 135–141. 593. Yang JW, Han BG, Kim BR, et al. Superior outcome of nafamostat mesilate as an anticoagulant in patients undergoing maintenance hemodialysis with intracerebral hemorrhage. Ren Fail 2009; 31: 668–675. 594. Maruyama H, Miyakawa Y, Gejyo F, et al. Anaphylactoid reaction induced by nafamostat mesilate in a hemodialysis patient. Nephron 1996; 74: 468–469. 595. Muto S, Imai M, Asano Y. Mechanisms of hyperkalemia caused by nafamostat mesilate.

**`pmid_23499048_p138_t2_c1`** *(text)*

Betjes MG, van Oosterom D, van Agteren M, et al. Regional citrate versus heparin anticoagulation during venovenous hemoﬁltration in patients at low risk for bleeding: similar hemoﬁlter survival but signiﬁcantly less bleeding. J Nephrol 2007; 20: 602–608. 601a. Hetzel GR, Schmitz, Wissing H, et al. Regional citrate versus systemic heparin for anticoagulation in critically ill patients on continuous venovenous haemoﬁltration: a prospective randomized multicentre trial. Nephrol Dial Transplant 2011; 26: 232–239. 601b. Park JS, Kim GH, Kang CM, et al.

**`pmid_23499048_p138_t3_c1`** *(text)*

606. Thoenen M, Schmid ER, Binswanger U, et al. Regional citrate anti- coagulation using a citrate-based substitution solution for continuous venovenous hemoﬁltration in cardiac surgery patients. Wien Klin Wochenschr 2002; 114: 108–114. 607. Uchino S, Bellomo R, Morimatsu H, et al. Continuous renal replacement therapy: a worldwide practice survey. The beginning and ending supportive therapy for the kidney (B.E.S.T. kidney) investigators. Intensive Care Med 2007; 33: 1563–1570. 608. Apsner R, Schwarzenhofer M, Derﬂer K, et al. Impairment of citrate meta- bolism in acute hepatic failure.

**`pmid_23499048_p138_t4_c1`** *(text)*

Detection of citrate overdose in critically ill patients on citrate-anticoagulated venovenous haemoﬁltration: use of ionised and total/ionised calcium. Clin Chem Lab Med 2006; 44: 962–966. 614. Davies HT, Leslie G, Pereira SM, et al. A randomized comparative crossover study to assess the affect on circuit life of varying pre-dilution volume associated with CVVH and CVVHDF. Int J Artif Organs 2008; 31: 221–227. 615. Holt AW, Bierer P, Bersten AD, et al. Continuous renal replacement therapy in critically ill patients: monitoring circuit function. Anaesth Intensive Care 1996; 24: 423–429. 616. Joannidis M, Kountchev J, Rauchenzauner M, et al. Enoxaparin vs.

**`pmid_23499048_p138_t5_c1`** *(text)*

621. de Pont AC, Oudemans-van Straaten HM, Roozendaal KJ, et al. Nadroparin versus dalteparin anticoagulation in high-volume, continuous venovenous hemoﬁltration: a double-blind, randomized, crossover study. Crit Care Med 2000; 28: 421–425. 622. Birnbaum J, Spies CD, Klotz E, et al. Iloprost for additional anticoagulation in continuous renal replacement therapy–a pilot study. Ren Fail 2007; 29: 271–277. 623. Kozek-Langenecker SA, Spiss CK, Gamsjager T, et al.

**`pmid_23499048_p138_t6_c1`** *(text)*

624. Fabbri LP, Nucera M, Al Malyan M, et al. Regional anticoagulation and antiaggregation for CVVH in critically ill patients: a prospective, randomized, controlled pilot study. Acta Anaesthesiol Scand 2010; 54: 92–97.

**`pmid_23499048_p138_t0_c2`** *(text)*

Davenport A, Tolwani A. Citrate anticoagulation for continuous renal replacement therapy (CRRT) in patients with acute kidney injury admitted to the intensive care unit. NDT Plus 2009; 2: 439–447. 586. Lim W, Cook DJ, Crowther MA.

**`pmid_23499048_p138_t1_c2`** *(text)*

594. Maruyama H, Miyakawa Y, Gejyo F, et al. Anaphylactoid reaction induced by nafamostat mesilate in a hemodialysis patient. Nephron 1996; 74: 468–469. 595. Muto S, Imai M, Asano Y. Mechanisms of hyperkalemia caused by nafamostat mesilate.

**`pmid_23499048_p138_t2_c2`** *(text)*

Hetzel GR, Schmitz, Wissing H, et al. Regional citrate versus systemic heparin for anticoagulation in critically ill patients on continuous venovenous haemoﬁltration: a prospective randomized multicentre trial. Nephrol Dial Transplant 2011; 26: 232–239. 601b. Park JS, Kim GH, Kang CM, et al.

**`pmid_23499048_p138_t3_c2`** *(text)*

Continuous renal replacement therapy: a worldwide practice survey. The beginning and ending supportive therapy for the kidney (B.E.S.T. kidney) investigators. Intensive Care Med 2007; 33: 1563–1570. 608. Apsner R, Schwarzenhofer M, Derﬂer K, et al. Impairment of citrate meta- bolism in acute hepatic failure.

**`pmid_23499048_p138_t4_c2`** *(text)*

Holt AW, Bierer P, Bersten AD, et al. Continuous renal replacement therapy in critically ill patients: monitoring circuit function. Anaesth Intensive Care 1996; 24: 423–429. 616. Joannidis M, Kountchev J, Rauchenzauner M, et al. Enoxaparin vs.

**`pmid_23499048_p138_t5_c2`** *(text)*

622. Birnbaum J, Spies CD, Klotz E, et al. Iloprost for additional anticoagulation in continuous renal replacement therapy–a pilot study. Ren Fail 2007; 29: 271–277. 623. Kozek-Langenecker SA, Spiss CK, Gamsjager T, et al.

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

