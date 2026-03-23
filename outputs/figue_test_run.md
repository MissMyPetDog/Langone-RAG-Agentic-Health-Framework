# Question

What does the evidence show about tau protein structure in chronic traumatic encephalopathy?

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=False, topn=5

---

## Answer

The problem in question involves understanding the structure of tau protein in the context of chronic traumatic encephalopathy (CTE). CTE is characterized by unique tau filaments, which differ in structure from those found in other tauopathies.

In CTE, tau protein filaments incorporate both 3-repeat (3R) and 4-repeat (4R) tau isoforms [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6)]. This distinguishes CTE from some other tauopathies, such as corticobasal degeneration, which features only 4R tau filaments. The structure of tau filaments in CTE is distinct from those seen in Alzheimer's disease and other related conditions. The detailed comparison of tau structures in various tauopathies highlights the distinct conformational folding and isoform composition of tau protein in CTE, which involves a mixed composition of isoforms and possibly distinct pathological impacts on cells [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6)].

1. Analyze structural details of tau protein in CTE through cryo-electron microscopy. This method allows for detailed visualization of the tau filaments, which could further elucidate the protein folding specifics in CTE [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6)].

2. Compare the tau composition by referencing data from Alzheimer's disease and Pick's disease. This can highlight differences in isoform presence and structural conformations between conditions, providing insight into disease-specific pathology [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6)].

3. Further study of the impacts of hydrophobic regions within tau filaments on cellular dysfunction may provide added insight into CTE-related neurodegeneration.

References:
- Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6): First-line evidence on tau isoform differences in CTE versus other tauopathies.

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

