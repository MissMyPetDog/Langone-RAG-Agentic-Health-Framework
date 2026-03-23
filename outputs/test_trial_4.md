# Question

Does sedentary behavior predict incident dementia in older adults?

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=True, topn=50

---

## Answer

The problem of whether sedentary behavior predicts incident dementia in older adults is addressed through a systematic review of epidemiological evidence. The systematic review studied observational research concerning the association between sedentary behavior as an exposure and cognitive function as an outcome in adults aged 40 years and older. Sedentary behavior was assessed to determine how it might influence cognitive decline, including the risk of all-cause dementia [Sedentary Behavior and Incident Dementia Among Older Adults (pmid_37698563_p2)].

Findings from the reviewed studies suggest a potential association between increased sedentary behavior and a decline in cognitive function over time, possibly increasing the risk of dementia. This suggests that public health interventions could consider targeting reductions in sedentary behavior, as well as promoting moderate-to-vigorous physical activity, to mitigate the risk of cognitive decline and dementia [Sedentary Behavior and Incident Dementia Among Older Adults (pmid_37698563_p2)].

Treatment Suggestions:
1. Increase Physical Activity: Encouraging moderate-to-vigorous physical activity could be beneficial in reducing the risk of dementia. This approach would aim to counteract the effects of sedentary behavior. It is appropriate in the absence of physical limitations preventing exercise. This recommendation is supported by evidence linking physical activity to improved cognitive outcomes [Sedentary Behavior and Incident Dementia Among Older Adults (pmid_37698563_p2)].

2. Reduce Sedentary Time: If increasing physical activity is not feasible due to physical constraints or personal choice, efforts to reduce total sedentary time can be considered as a standalone strategy. While specific interventions were not analyzed, general reductions in sedentary behavior could potentially slow cognitive decline [Sedentary Behavior and Incident Dementia Among Older Adults (pmid_37698563_p2)].

3. Behavioral Interventions: If direct reduction of sedentary behavior or increase in physical activity is not achievable, structured behavioral interventions that include cognitive training exercises might help in maintaining cognitive health. This third-line strategy may be particularly useful for individuals with significant mobility issues [Sedentary Behavior and Incident Dementia Among Older Adults (pmid_37698563_p2)].

References:
- Sedentary Behavior and Incident Dementia Among Older Adults (pmid_37698563_p2): First-line therapy evidence for addressing the link between sedentary behavior and cognitive outcomes.

---

## Used Sources (with context)

### === DOC pmid_30894745 / Novel tau filament fold in chronic traumatic encephalopathy encloses hydrophobic molecules. / pmid_30894745_p3 ===

**`pmid_30894745_p3_t0_c0`** *(text)*

annotation. The ‘–downdb’ argument can be utilized for downloading necessary ﬁles automatically, if the computer is connected to the Internet. The ‘wget’ system command will be utilized for downloading, or the Net::Ftp/ LWP::UserAgent modules (standard Perl modules installed in most systems by default) can be alternatively utilized. The users can specify different genome builds, such as hg18 (human), mm9 (mouse) or bosTau4 (cow), as long as they are available from the UCSC Genome Browser annotation databases. When performing gene-based annotations by Ensembl gene deﬁnitions (13), ANNOVAR will download the FASTA sequences from Ensembl as they were not available from the UCSC Genome Browser. For region-based annotations, ANNOVAR needs to download annotation databases from the various UCSC Genome Browser tables, based on a user-speciﬁed track name. Alternatively, users can specify a custom-built an- notation database conforming to Generic Feature Format 3 (GFF3), and ANNOVAR can identify variants over- lapping with features annotated in the given GFF3 ﬁle. For ﬁlter-based annotations, for example, comparing mu- tations to those detected in the 1000 Genomes Project or dbSNP, ANNOVAR will download speciﬁc ﬁles from the corresponding websites.

**`pmid_30894745_p3_t1_c0`** *(text)*

Scan annotation database While reading variants from input ﬁle, ANNOVAR scans the gene annotation database stored at local disk, and identiﬁes intronic variants, exonic variants, intergenic variants, 50/30-UTR variants, splicing site variants and upstream/downstream variants (less than a threshold away from a transcript, by default 1 kb). For intergenic variants, the closest two genes and the distances to them are reported. For exonic variants, ANNOVAR scans annotated mRNA sequences to identify and report amino acid changes, as well as stop-gain or stop-loss mutations. ANNOVAR can also perform region-based annotations on many types of annotation tracks, such as the most conserved elements and the predicted transcription factor binding sites. These annotations must be downloaded by ANNOVAR, before they can be utilized. Finally, ANNOVAR can ﬁlter speciﬁc variants such as SNPs with >1% frequency in the 1000 Genomes Project, or non-synonymous SNPs with SIFT scores >0.05. To automate the procedure of reducing large amounts of variants into a small subset of functionally import- ant variants, a script (auto_annovar.pl) is provided in the ANNOVAR package. By default, auto_annovar.pl performs a multi-step procedure by executing ANNOVAR multiple times, each time with several differ- ent command line parameters, and generates a ﬁnal output ﬁle containing the most likely causal variants and their corresponding candidate genes.

**`pmid_30894745_p3_t2_c0`** *(text)*

Compilation of ‘dispensable’ genes Based on the hypothesis that genes with high frequency of non-sense (stop-gain) mutations in population are unlikely to be causal for rare Mendelian diseases, we compiled a list of such ‘dispensable’ genes using data from the 1000 Genomes Project. For the CEU, YRI and JPT+CHB population separately, we identify genes that have non-sense mutations with combined minor allele fre- quency (MAF) >1%. For example, if two nonsense mu- tations in the same gene have MAF of 0.5 and 0.8% in CEU populations, this gene will be regarded as a dis- pensable gene. This analysis resulted in the identiﬁcation of a total of 2064 genes from the 1000 Genomes Project. We caution that genes may fall within this list due to sequencing errors or alignment errors; for example, if the gene has many pseudogenes or if it is present within a segmental duplication. This list (10% of all annotated human genes) is useful as a ﬁltering step to further trim down potential candidate genes for Mendelian diseases. Compilation of two synthetic data sets To illustrate the utility of ANNOVAR in identifying causal genes for Mendelian diseases with recessive inher- itance, we synthesized a whole-genome data set with 4.2 million SNVs and 0.5 million indels.

**`pmid_30894745_p3_t3_c0`** *(text)*

We tested the variants reduction procedure on this data set using ANNOVAR, to examine whether we can identify a small subset of candidate genes that include the causal gene DHODH. To illustrate the utility of ANNOVAR in identifying causal genes for Mendelian diseases with dominant inher- itance, we synthesized whole-exome data sets. Since exome data for four Freeman–Sheldon cases were not available to us, we downloaded the exome data for eight HapMap subjects reported in (11). We then extracted the exome data for the ﬁrst four subjects, including two Yoruba subjects (NA18507, NA18517) and two European Americans (NA12156 and NA12878). We next added the four known causal mutations to each of the four HapMap subjects (three C–>T mutations at chr17:10485359 and one C–>T mutation at chr17:10485360, representing R672H and R672C mutations in MYH3). We tested whether ANNOVAR can identify MYH3 as the causal gene by examining exomes from these four subjects. RESULTS AND DISCUSSION Gene-based, region-based and ﬁlter-based annotation of genetic variants To demonstrate the functionality and output of ANNOVAR, we analyzed the input ﬁle shown in Table 1. We applied gene-based annotation procedure using RefSeq gene deﬁnitions (15), though the UCSC Genes PAGE 3 OF 7 Nucleic Acids Research, 2010, Vol.

**`pmid_30894745_p3_t4_c0`** *(text)*

16 e164

**`pmid_30894745_p3_t0_c1`** *(text)*

For region-based annotations, ANNOVAR needs to download annotation databases from the various UCSC Genome Browser tables, based on a user-speciﬁed track name. Alternatively, users can specify a custom-built an- notation database conforming to Generic Feature Format 3 (GFF3), and ANNOVAR can identify variants over- lapping with features annotated in the given GFF3 ﬁle. For ﬁlter-based annotations, for example, comparing mu- tations to those detected in the 1000 Genomes Project or dbSNP, ANNOVAR will download speciﬁc ﬁles from the corresponding websites. ANNOVAR can also download pre-computed SIFT scores for all human non- synonymous mutations, to help annotate human exomes by ﬁlter-based annotation procedure.

**`pmid_30894745_p3_t1_c1`** *(text)*

To automate the procedure of reducing large amounts of variants into a small subset of functionally import- ant variants, a script (auto_annovar.pl) is provided in the ANNOVAR package. By default, auto_annovar.pl performs a multi-step procedure by executing ANNOVAR multiple times, each time with several differ- ent command line parameters, and generates a ﬁnal output ﬁle containing the most likely causal variants and their corresponding candidate genes. For recessive diseases, this list can be further trimmed down to include genes with multiple variants that are predicted to be functionally important.

**`pmid_30894745_p3_t2_c1`** *(text)*

This list (10% of all annotated human genes) is useful as a ﬁltering step to further trim down potential candidate genes for Mendelian diseases. Compilation of two synthetic data sets To illustrate the utility of ANNOVAR in identifying causal genes for Mendelian diseases with recessive inher- itance, we synthesized a whole-genome data set with 4.2 million SNVs and 0.5 million indels. These variants include all variants generated by Illumina on a male Yoruba subject (ftp://ftp.sanger.ac.uk/pub/rd/ NA18507/) (14), as well as two known causal mutations for Miller syndrome (G->A mutation at chr16: 70608443 and G->C mutation at chr16: 70612611, representing G152R and G202A in the DHODH gene).

**`pmid_30894745_p3_t3_c1`** *(text)*

We tested whether ANNOVAR can identify MYH3 as the causal gene by examining exomes from these four subjects. RESULTS AND DISCUSSION Gene-based, region-based and ﬁlter-based annotation of genetic variants To demonstrate the functionality and output of ANNOVAR, we analyzed the input ﬁle shown in Table 1. We applied gene-based annotation procedure using RefSeq gene deﬁnitions (15), though the UCSC Genes PAGE 3 OF 7 Nucleic Acids Research, 2010, Vol. 38, No.

**`pmid_30894745_p3_t0_c2`** *(text)*

Alternatively, users can specify a custom-built an- notation database conforming to Generic Feature Format 3 (GFF3), and ANNOVAR can identify variants over- lapping with features annotated in the given GFF3 ﬁle. For ﬁlter-based annotations, for example, comparing mu- tations to those detected in the 1000 Genomes Project or dbSNP, ANNOVAR will download speciﬁc ﬁles from the corresponding websites. ANNOVAR can also download pre-computed SIFT scores for all human non- synonymous mutations, to help annotate human exomes by ﬁlter-based annotation procedure.

**`pmid_30894745_p3_t2_c2`** *(text)*

Compilation of two synthetic data sets To illustrate the utility of ANNOVAR in identifying causal genes for Mendelian diseases with recessive inher- itance, we synthesized a whole-genome data set with 4.2 million SNVs and 0.5 million indels. These variants include all variants generated by Illumina on a male Yoruba subject (ftp://ftp.sanger.ac.uk/pub/rd/ NA18507/) (14), as well as two known causal mutations for Miller syndrome (G->A mutation at chr16: 70608443 and G->C mutation at chr16: 70612611, representing G152R and G202A in the DHODH gene).

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p5 ===

**`pmid_32050258_p5_t0_c0`** *(text)*

Find articles by Shigeo Murayama 4, Bernardino Ghetti Bernardino Ghetti 3Department of Pathology and Laboratory Medicine, Indiana University School of Medicine, Indianapolis, IN 46202, USA Find articles by Bernardino Ghetti 3, Masato Hasegawa Masato Hasegawa 2Department of Dementia and Higher Brain Function, Tokyo Metropolitan Institute of Medical Science, Tokyo, 156-8506, Japan. Find articles by Masato Hasegawa 2, Michel Goedert Michel Goedert 1MRC Laboratory of Molecular Biology, Cambridge, CB2 0QH, United Kingdom Find articles by Michel Goedert 1,*, Sjors HW Scheres Sjors HW Scheres 1MRC Laboratory of Molecular Biology, Cambridge, CB2 0QH, United Kingdom Find articles by Sjors HW Scheres 1,* •  Author information •  Article notes •  Copyright and License information PMCID: PMC7148158  NIHMSID: NIHMS1556889  EMSID: EMS85703  PMID: 32050258 The publisher's version of this article is available at Nature

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p6 ===

**`pmid_32050258_p6_t0_c0`** *(text)*

Abstract Corticobasal degeneration (CBD) is a neurodegenerative tauopathy that is characterised by motor and cognitive disturbances (1–3). A higher frequency of the H1 haplotype of MAPT, the tau gene, is present in cases of CBD than in controls (4,5) and genome-wide association studies have identified additional risk factors (6). By histology, astrocytic plaques are diagnostic of CBD (7,8), as are detergent-insoluble tau fragments of 37 kDa by SDS-PAGE (9). Like progressive supranuclear palsy (PSP), globular glial tauopathy (GGT) and argyrophilic grain disease (AGD) (10), CBD is characterised by abundant filamentous tau inclusions that are made of isoforms with four microtubule-binding repeats (4R) (11–15). This distinguishes 4R tauopathies from Pick’s disease, filaments of which are made of three-repeat (3R) tau isoforms, and from Alzheimer’s disease and chronic traumatic encephalopathy (CTE), where both 3R and 4R tau isoforms are found in the filaments (16). Here we report the structures of tau filaments extracted from the brains of three individuals with CBD using electron cryo-microscopy (cryo-EM). They were identical between cases, but distinct from those of Alzheimer’s disease, Pick’s disease and CTE (17–19).

**`pmid_32050258_p6_t1_c0`** *(text)*

CBD is the first 4R tauopathy with filaments of known structure. We extracted tau filaments from the brains of three individuals with a neuropathologically confirmed diagnosis of CBD. Abundant neuronal inclusions and astrocytic plaques were stained by antibodies specific for 4R tau (Figure 1a–c) and for hyperphosphorylated tau (Figure 1e), as well as by Gallyas-Braak silver (Figure 1f). Antibodies against 3R tau failed to give specific staining (Figure 1d) Astrocytic tau inclusions were more numerous in basal ganglia than in cerebral cortex.

**`pmid_32050258_p6_t2_c0`** *(text)*

By immunoblotting of sarkosyl-insoluble fractions, two major tau bands of 64 and 68 kDa were stained by an antibody specific for 4R tau, as were two minor

**`pmid_32050258_p6_t0_c1`** *(text)*

This distinguishes 4R tauopathies from Pick’s disease, filaments of which are made of three-repeat (3R) tau isoforms, and from Alzheimer’s disease and chronic traumatic encephalopathy (CTE), where both 3R and 4R tau isoforms are found in the filaments (16). Here we report the structures of tau filaments extracted from the brains of three individuals with CBD using electron cryo-microscopy (cryo-EM). They were identical between cases, but distinct from those of Alzheimer’s disease, Pick’s disease and CTE (17–19). The core of CBD filaments comprises residues K274-E380 of tau, spanning the last residue of R1, the whole of R2, R3 and R4, as well as 12 amino acids after R4. It adopts a novel four-layered fold, which encloses a large non-proteinaceous density. The latter is surrounded by the side chains of lysine residues 290 and 294 from R2 and 370 from the sequence after R4.

**`pmid_32050258_p6_t1_c1`** *(text)*

We extracted tau filaments from the brains of three individuals with a neuropathologically confirmed diagnosis of CBD. Abundant neuronal inclusions and astrocytic plaques were stained by antibodies specific for 4R tau (Figure 1a–c) and for hyperphosphorylated tau (Figure 1e), as well as by Gallyas-Braak silver (Figure 1f). Antibodies against 3R tau failed to give specific staining (Figure 1d) Astrocytic tau inclusions were more numerous in basal ganglia than in cerebral cortex.

**`pmid_32050258_p6_t0_c2`** *(text)*

The core of CBD filaments comprises residues K274-E380 of tau, spanning the last residue of R1, the whole of R2, R3 and R4, as well as 12 amino acids after R4. It adopts a novel four-layered fold, which encloses a large non-proteinaceous density. The latter is surrounded by the side chains of lysine residues 290 and 294 from R2 and 370 from the sequence after R4.

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p7 ===

**`pmid_32050258_p7_t0_c0`** *(text)*

bands of 37 kDa (Figure 1g). Immunogold negative-stain EM used filaments extracted from frontal cortex and putamen of CBD cases 1–3, as well as from globus pallidus and thalamus of CBD case 3. Antibodies specific for the N-terminus, R1, R2, R3 and R4 and the C-terminus of tau indicated that the cores of CBD filaments share epitopes of R2, R3 and R4 (Extended Data Figures 1 and 2). This is consistent with the estimated lengths of trypsin-resistant cores of CBD filaments (20). Narrow and wide tau filaments were present (Figure 1h), in agreement with previous findings (21). Narrow filaments have a helical twist with a crossover distance of approximately 1,000 Å, a minimal width of 80 Å and a maximal width of 130 Å. Wide filaments have a crossover distance of approximately 1,400 Å and a maximal width of 260 Å, with a similar minimal width as that of narrow tau filaments. We named these filaments Type I (narrow) and Type II (wide) CBD filaments, respectively. Co-pathologies are often found in CBD (22,23). Small amounts of assembled TDP-43 were present in frontal cortex of CBD cases 1 and 2; CBD case 3 was negative (Extended Data Figure 3). It has been reported that C9orf72 intermediate repeat expansions are associated with a subset of cases of CBD (24).

**`pmid_32050258_p7_t1_c0`** *(text)*

Abundant α-synuclein inclusions were not present in CBD cases 1–3, nor were inclusions positive for FUS or positive for dipeptide repeats. Figure 1. Filamentous tau pathology of CBD. [image] Open in a new tab (a-f), Staining of neuronal inclusions, neuropil threads and astrocytic plaques in the frontal cortex of CBD cases 1–3 by antibody RD4 (specific for 4R tau, brown) (a-c), and in the frontal cortex of case 3 by antibody AT8 (pS202, pT205 tau, brown) (e)

**`pmid_32050258_p7_t0_c1`** *(text)*

Co-pathologies are often found in CBD (22,23). Small amounts of assembled TDP-43 were present in frontal cortex of CBD cases 1 and 2; CBD case 3 was negative (Extended Data Figure 3). It has been reported that C9orf72 intermediate repeat expansions are associated with a subset of cases of CBD (24). Such expansions were not present in CBD cases 1–3. CBD case 1 had 2 repeats on each allele, CBD case 2 had also 2 repeats on each allele and CBD case 3 had 2 repeats on one allele and 11 repeats on the other. Staining for Aβ in frontal cortex was stage A for CBD case 1 and stage 0 for CBD cases 2 and 3.

**`pmid_32050258_p7_t1_c1`** *(text)*

Filamentous tau pathology of CBD. [image] Open in a new tab (a-f), Staining of neuronal inclusions, neuropil threads and astrocytic plaques in the frontal cortex of CBD cases 1–3 by antibody RD4 (specific for 4R tau, brown) (a-c), and in the frontal cortex of case 3 by antibody AT8 (pS202, pT205 tau, brown) (e)

**`pmid_32050258_p7_t0_c2`** *(text)*

Such expansions were not present in CBD cases 1–3. CBD case 1 had 2 repeats on each allele, CBD case 2 had also 2 repeats on each allele and CBD case 3 had 2 repeats on one allele and 11 repeats on the other. Staining for Aβ in frontal cortex was stage A for CBD case 1 and stage 0 for CBD cases 2 and 3.

### === DOC pmid_37698563 / Sedentary Behavior and Incident Dementia Among Older Adults. / pmid_37698563_p2 ===

**`pmid_37698563_p2_fig_0_c0`** *(image)*

![page_2_fig_0.jpeg](../data/raw/pmid_37698563/page_2_fig_0.jpeg)

**`pmid_37698563_p2_t0_c0`** *(text)*

determining whether public health should focus on reducing sedentary behaviour, increasing moderate-to-vigorous physical activity or both to reduce all-cause dementia prevalence. Thus, our objective was to systematically review the epidemiological evidence regarding how sedentary behaviour is associated with cognitive function throughout the adult lifespan. METHODS Summary of search strategy We conducted a systematic review regarding the association between sedentary behaviour and cognitive function. In accord- ance with the Preferred Reporting Items for Systematic Reviews and Meta-Analyses (PRISMA) statement,21 we searched PubMed, PsycINFO, EBSCO and Web of Science between 1 January 1990 and 6 February 2016. Included in our search terms were the following keywords: sedentary behaviour terms (sedentary behaviour, physical inactivity, television time, TV time, screen time); cognition terms (cognition, cognitive func- tion, brain function, executive function, memory, dementia, Alzheimer’s disease) and age terms (older adults, elders, elderly, ageing, aged, 40+ years). This process was repeated until all search term combinations were performed. A sample of the search strategy used for studies investigating the association between sedentary behaviour and cognitive function is provided in ﬁgure 1A.

**`pmid_37698563_p2_t1_c0`** *(text)*

Articles mentioning sedentary behaviour and cogni- tion in either the title or abstract were initially included for full- text review. Inclusion and exclusion criteria We included studies if they were (1) observational studies (ie, cohort, case-control or cross-sectional); (2) peer reviewed and (3) published in the English language between 1 January 1990 and 6 February 2016. All studies included clearly described participants as adults aged 40 years and older at baseline assessment and mea- sured sedentary behaviour at baseline assessment or over time with the purpose of assessing risk (ie, exposure). Additionally, the studies included measured cognitive function at baseline assess- ment or over time with the purpose of determining change asso- ciated with increased sedentary behaviour (ie, outcome). We excluded articles if they were (1) not peer reviewed and (2) not published in the English language. Since we were only interested in observational studies, interventions designed to reduce sedentary behaviour were not included. Data extraction Two authors (RSF and JCD) initially screened and identiﬁed studies based on the study title and abstract. Duplicates and arti- cles failing to meet inclusion criteria were removed.

**`pmid_37698563_p2_t2_c0`** *(text)*

Data were extracted from the included articles using a custom data extraction form developed by RSF and JCD. We extracted the following categories: (1) study design; (2) participant characteristics, setting and length of follow-up; (3) measure of exposure (ie, sedentary behaviour); (4) measure of outcome (ie, cognitive function) and (5) main ﬁndings. For exposure measures (ie, sedentary behaviour), we extracted the (1) instrument name; (2) exposure deﬁnition (eg, sedentary Figure 1 (A) Simpliﬁed search strategy. (B) Flow chart of study selection. 801 Falck RS, et al. Br J Sports Med 2017;51:800–811. doi:10.1136/bjsports-2015-095551 Review Protected by copyright, including for uses related to text and data mining, AI training, and similar technologies. . at NYU Langone Medical Center



on March 1, 2026



http://bjsm.bmj.com/ Downloaded from 6 May 2016. 10.

**`pmid_37698563_p2_t3_c0`** *(text)*

1136/bjsports-2015-095551 on Br J Sports Med: first published as

**`pmid_37698563_p2_t0_c1`** *(text)*

Included in our search terms were the following keywords: sedentary behaviour terms (sedentary behaviour, physical inactivity, television time, TV time, screen time); cognition terms (cognition, cognitive func- tion, brain function, executive function, memory, dementia, Alzheimer’s disease) and age terms (older adults, elders, elderly, ageing, aged, 40+ years). This process was repeated until all search term combinations were performed. A sample of the search strategy used for studies investigating the association between sedentary behaviour and cognitive function is provided in ﬁgure 1A. Study selection We selected peer-reviewed, published and observational studies that included adults aged 40 years and older that measured sed- entary behaviour as an exposure and cognitive function as an outcome.

**`pmid_37698563_p2_t1_c1`** *(text)*

We excluded articles if they were (1) not peer reviewed and (2) not published in the English language. Since we were only interested in observational studies, interventions designed to reduce sedentary behaviour were not included. Data extraction Two authors (RSF and JCD) initially screened and identiﬁed studies based on the study title and abstract. Duplicates and arti- cles failing to meet inclusion criteria were removed. The remain- ing full-text articles were reviewed by RSF and JCD to determine eligibility. Any disagreements were resolved by a third reviewer (TL-A). Two raters (RSF and JCD) independently extracted data from all articles included; discrepancies were discussed and reviewed by a third party (TL-A).

**`pmid_37698563_p2_t2_c1`** *(text)*

Br J Sports Med 2017;51:800–811. doi:10.1136/bjsports-2015-095551 Review Protected by copyright, including for uses related to text and data mining, AI training, and similar technologies. . at NYU Langone Medical Center



on March 1, 2026



http://bjsm.bmj.com/ Downloaded from 6 May 2016. 10.

**`pmid_37698563_p2_t0_c2`** *(text)*

A sample of the search strategy used for studies investigating the association between sedentary behaviour and cognitive function is provided in ﬁgure 1A. Study selection We selected peer-reviewed, published and observational studies that included adults aged 40 years and older that measured sed- entary behaviour as an exposure and cognitive function as an outcome.

**`pmid_37698563_p2_t1_c2`** *(text)*

The remain- ing full-text articles were reviewed by RSF and JCD to determine eligibility. Any disagreements were resolved by a third reviewer (TL-A). Two raters (RSF and JCD) independently extracted data from all articles included; discrepancies were discussed and reviewed by a third party (TL-A).

