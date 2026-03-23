# Question

COVID-19 dexamethasone hospitalized and side effects

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=False, topn=5

---

## Answer

The use of dexamethasone in hospitalized COVID-19 patients has been studied to evaluate its effectiveness and potential side effects. In the context of the COVID-19 pandemic, dexamethasone, a corticosteroid, has been shown to benefit patients by reducing inflammation that can lead to severe respiratory symptoms.

**Evidence Summary:**
The RECOVERY trial documented that dexamethasone reduced the 28-day mortality rate for patients hospitalized with COVID-19 who were receiving respiratory support. The drug was particularly beneficial for those on mechanical ventilation or receiving supplemental oxygen, while no benefit was observed for patients not requiring respiratory support [Dexamethasone in Hospitalized Patients with Covid-19 (pmid_32678530_p73)].

**Adverse Effects:**
Potential side effects of dexamethasone include hyperglycemia, increased risk of infections, and possible exacerbation of pre-existing conditions due to its immunosuppressive effects. The drug can also lead to side effects like weight gain, mood swings, and hypertension, especially with long-term use.

**Treatment Suggestions:**

1. **Dexamethasone**: 
   - **Appropriate Use**: In hospitalized COVID-19 patients who require supplemental oxygen or invasive mechanical ventilation. Evidence suggests it reduces mortality in these groups [Dexamethasone in Hospitalized Patients with Covid-19 (pmid_32678530_p73)].
   - **Avoid When**: Should be avoided in COVID-19 patients who do not require oxygen support due to a lack of benefit. Caution is necessary in patients with conditions worsened by corticosteroids, such as uncontrolled diabetes or active infections.

2. **Alternative Corticosteroids**:
   - **Appropriate Use**: Consider if dexamethasone is contraindicated or unavailable. Similar corticosteroids might be used adhering to specific dosing guidelines for COVID-19 if supported by further studies.
   - **Avoid When**: There is insufficient evidence supporting their equivalence to dexamethasone for COVID-19 beyond similar glucocorticoids with better side effect profiles in specific conditions.

3. **Non-Corticosteroidal Immunomodulators**:
   - **Appropriate Use**: Consider these when corticosteroids are contraindicated or cause severe side effects. More evidence is needed, but IL-6 inhibitors may offer benefits and should be considered in specific clinical scenarios with concurrent severe inflammation.
   - **Avoid When**: When there is a risk of severe infections due to their immunosuppressive actions or lack of definitive evidence in the context of COVID-19.

**Conclusion:**
Dexamethasone is an effective treatment for hospitalized COVID-19 patients on respiratory support. Its use should consider the potential side effects and patient-specific contraindications. If dexamethasone is not suitable, alternative corticosteroids or other immunomodulatory treatments, while less evidenced, may be considered with caution.

**References:**
- Dexamethasone in Hospitalized Patients with Covid-19 (pmid_32678530_p73): First-line therapy evidence and safety/interaction data.
- Additional context on corticosteroid alternatives and their potential use cases would be beneficial.

---

## Used Sources (with context)

### === DOC pmid_30894745 / Novel tau filament fold in chronic traumatic encephalopathy encloses hydrophobic molecules. / pmid_30894745_p1 ===

**`pmid_30894745_p1_t0_c0`** *(text)*

ANNOVAR: functional annotation of genetic variants from high-throughput sequencing data Kai Wang1,*, Mingyao Li2 and Hakon Hakonarson1,3 1Center for Applied Genomics, Children’s Hospital of Philadelphia, 2Department of Biostatistics and Epidemiology and 3Department of Pediatrics, University of Pennsylvania, Philadelphia, PA 19104, USA Received March 27, 2010; Revised June 2, 2010; Accepted June 18, 2010 ABSTRACT High-throughput sequencing platforms are genera- ting massive amounts of genetic variation data for diverse genomes, but it remains a challenge to pinpoint a small subset of functionally important variants. To fill these unmet needs, we developed the ANNOVAR tool to annotate single nucleotide variants (SNVs) and insertions/deletions, such as examining their functional consequence on genes, inferring cytogenetic bands, reporting functional im- portance scores, finding variants in conserved regions, or identifying variants reported in the 1000 Genomes Project and dbSNP. ANNOVAR can utilize annotation databases from the UCSC Genome Browser or any annotation data set conforming to Generic Feature Format version 3 (GFF3). We also illustrate a ‘variants reduction’ protocol on 4.7 million SNVs and indels from a human genome, including two causal mutations for Miller syndrome, a rare recessive disease.

**`pmid_30894745_p1_t1_c0`** *(text)*

Using a desktop computer, ANNOVAR requires 4 min to perform gene-based annotation and 15 min to perform variants reduc- tion on 4.7 million variants, making it practical to handle hundreds of human genomes in a day. ANNOVAR is freely available at http://www. openbioinformatics.org/annovar/. INTRODUCTION High-throughput sequencing data have been produced at unprecedented rates for diverse genomes. There is a strong need for novel informatics and analytical strategies, including methods for sequencing reads alignment, variant identiﬁcation, genotype calling and association tests, in order to take advantage of the massive amounts of sequencing data. There have been dozens of short read alignment software available now with different function- alities (1), as well as several single nucleotide variants (SNV) and copy number variant (CNV) calling algorithms (2). However, there is a paucity of methods that can sim- ultaneously handle a large number of called variants (typ- ically >3 million variants for a given human genome) and annotate their functional impacts, despite the fact that this is an important task in many sequencing applications. Even when sequencing only exonic regions for Mendelian diseases such as Freeman–Sheldon syndrome, each subject still carries a total of 20 000 variants, but only two variants in trans are the true disease causal mu- tations (3).

**`pmid_30894745_p1_t2_c0`** *(text)*

Several reasons motivate us to develop a functional annotation pipeline for genetic variants. First, although companies that manufacture sequencing machines or provide sequencing services typically offer software for functional annotation, these software are usually sequencing platform-speciﬁc, and cannot be extended to handle users’ speciﬁc needs (such as using different genome builds or gene annotations). Second, although several databases have been developed for the functional annotation of SNPs or CNVs (4–6), most of them are limited to known variants, typically those reported in dbSNP or CNV databases. We note that some excep- tions exist (7), for example, the F-SNP tool (8) and Seattle Seq tool (http://gvs.gs.washington.edu/SeattleSeq Annotation/) can be used for annotation of novel SNPs. Third, several previously developed mutation prediction algorithms, such as SIFT (9) and PolyPhen (10), require building multiple alignments on sequence databases, can only handle non-synonymous mutations, and are difﬁcult to scale up to many model organism genomes. Nevertheless, for human genomes, SIFT/PolyPhen scores for all possible non-synonymous mutations can be *To whom correspondence should be addressed.

**`pmid_30894745_p1_t3_c0`** *(text)*

This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/ by-nc/2.5), which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.

**`pmid_30894745_p1_t0_c1`** *(text)*

To fill these unmet needs, we developed the ANNOVAR tool to annotate single nucleotide variants (SNVs) and insertions/deletions, such as examining their functional consequence on genes, inferring cytogenetic bands, reporting functional im- portance scores, finding variants in conserved regions, or identifying variants reported in the 1000 Genomes Project and dbSNP. ANNOVAR can utilize annotation databases from the UCSC Genome Browser or any annotation data set conforming to Generic Feature Format version 3 (GFF3). We also illustrate a ‘variants reduction’ protocol on 4.7 million SNVs and indels from a human genome, including two causal mutations for Miller syndrome, a rare recessive disease. Through a stepwise pro- cedure, we excluded variants that are unlikely to be causal, and identified 20 candidate genes including the causal gene.

**`pmid_30894745_p1_t1_c1`** *(text)*

However, there is a paucity of methods that can sim- ultaneously handle a large number of called variants (typ- ically >3 million variants for a given human genome) and annotate their functional impacts, despite the fact that this is an important task in many sequencing applications. Even when sequencing only exonic regions for Mendelian diseases such as Freeman–Sheldon syndrome, each subject still carries a total of 20 000 variants, but only two variants in trans are the true disease causal mu- tations (3). Therefore, identifying a small subset of func- tionally important variants from large amounts of sequencing data is important to pinpoint potential disease causal genes and causal mutations.

**`pmid_30894745_p1_t2_c1`** *(text)*

We note that some excep- tions exist (7), for example, the F-SNP tool (8) and Seattle Seq tool (http://gvs.gs.washington.edu/SeattleSeq Annotation/) can be used for annotation of novel SNPs. Third, several previously developed mutation prediction algorithms, such as SIFT (9) and PolyPhen (10), require building multiple alignments on sequence databases, can only handle non-synonymous mutations, and are difﬁcult to scale up to many model organism genomes. Nevertheless, for human genomes, SIFT/PolyPhen scores for all possible non-synonymous mutations can be *To whom correspondence should be addressed. Tel: +1 215 426 1256; Fax: +1 267 426 0363; Email: kai@openbioinformatics.org Published online 3 July 2010 Nucleic Acids Research, 2010, Vol. 38, No. 16 e164 doi:10.1093/nar/gkq603  The Author(s) 2010. Published by Oxford University Press.

**`pmid_30894745_p1_t0_c2`** *(text)*

ANNOVAR can utilize annotation databases from the UCSC Genome Browser or any annotation data set conforming to Generic Feature Format version 3 (GFF3). We also illustrate a ‘variants reduction’ protocol on 4.7 million SNVs and indels from a human genome, including two causal mutations for Miller syndrome, a rare recessive disease. Through a stepwise pro- cedure, we excluded variants that are unlikely to be causal, and identified 20 candidate genes including the causal gene.

**`pmid_30894745_p1_t2_c2`** *(text)*

Nevertheless, for human genomes, SIFT/PolyPhen scores for all possible non-synonymous mutations can be *To whom correspondence should be addressed. Tel: +1 215 426 1256; Fax: +1 267 426 0363; Email: kai@openbioinformatics.org Published online 3 July 2010 Nucleic Acids Research, 2010, Vol. 38, No. 16 e164 doi:10.1093/nar/gkq603  The Author(s) 2010. Published by Oxford University Press.

### === DOC pmid_32678530 / Dexamethasone in Hospitalized Patients with Covid-19. / pmid_32678530_p73 ===

**`pmid_32678530_p73_t0_c0`** *(text)*

part by the NIAID of the NIHunder award numbers UM1AI148684, UM1AI148576, UM1AI148573, UM1AI148575, UM1AI148452, UM1AI148685, UM1AI148450, and UM1AI148689. The trial has also been funded in part by the governments of Denmark, Japan, Mexico, and Singapore. The trial site in South Korea received funding from the Seoul National University Hospital. Support for the London International Coordinating Centre was also provided by the United Kingdom Medical Research Council (MRC_UU_12023/23). Disclosure forms provided by the authors are available with the full text of this article at NEJM.org. References 1.Helmy YA, Fawzy M, Elaswad A, Sobieh A, Kenney SP, Shehata AA. The COVID-19 pandemic: a comprehensive review of taxonomy, genetics, epidemiology, diagnosis, treatment, and control. J Clin Med 2020;9(4):E1225-E1225. [DOI] [PMC free article] [PubMed] [Google Scholar] 2.Cao B, Wang Y, Wen D, et al. A trial of lopinavir–ritonavir in adults hospitalized with severe Covid-19. N Engl J Med 2020;382:1787-1799. [DOI] [PMC free article] [PubMed] [Google Scholar] 3.Borba MGS, Val FFA, Sampaio VS, et al. Effect of high vs low doses of chloroquine diphosphate as adjunctive therapy for patients hospitalized with severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) infection: a randomized clinical trial.

**`pmid_32678530_p73_t1_c0`** *(text)*

Sheahan TP, Sims AC, Leist SR, et al. Comparative therapeutic efficacy of remdesivir and combination lopinavir, ritonavir, and interferon beta against MERS-CoV. Nat Commun 2020;11:222-222. [DOI] [PMC free article] [PubMed] [Google Scholar] 6.Agostini ML, Andres EL, Sims AC, et al.

**`pmid_32678530_p73_t2_c0`** *(text)*

Coronavirus

**`pmid_32678530_p73_t0_c1`** *(text)*

[DOI] [PMC free article] [PubMed] [Google Scholar] 3.Borba MGS, Val FFA, Sampaio VS, et al. Effect of high vs low doses of chloroquine diphosphate as adjunctive therapy for patients hospitalized with severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) infection: a randomized clinical trial. JAMA Netw Open 2020;3(4):e208857-e208857. [DOI] [PMC free article] [PubMed] [Google Scholar] 4.The RECOVERY Collaborative Group. Dexamethasone in hospitalized patients with Covid-19 — preliminary report. N Engl J Med. DOI: 10.1056/NEJMoa2021436. [DOI] [PMC free article] [PubMed] 5.

**`pmid_32678530_p73_t0_c2`** *(text)*

JAMA Netw Open 2020;3(4):e208857-e208857. [DOI] [PMC free article] [PubMed] [Google Scholar] 4.The RECOVERY Collaborative Group. Dexamethasone in hospitalized patients with Covid-19 — preliminary report. N Engl J Med. DOI: 10.1056/NEJMoa2021436. [DOI] [PMC free article] [PubMed] 5.

