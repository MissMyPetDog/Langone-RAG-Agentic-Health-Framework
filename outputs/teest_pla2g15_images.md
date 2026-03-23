# Question

tau filament structure chronic traumatic encephalopathy cryo-EM

**Vectors:** `data/real_vectors.jsonl` | topk=8, rerank=True, topn=50

---

## Answer

The inquiry revolves around the use of cryo-electron microscopy (cryo-EM) to discern the tau filament structures involved in chronic traumatic encephalopathy (CTE), a neurodegenerative tauopathy. While the information provided delves into the cryo-EM derived structures of tau filaments in corticobasal degeneration (CBD), it also comments on tau filament inclusions in CTE, though primarily in comparative terms. The structures of tau filaments in tauopathies can significantly differ, impacting their pathogenicity and potential treatment targets.

### Problem Summary
The goal is to understand the cryo-EM findings related to tau filament structures in CTE, investigating whether structural insights can lead to targeted therapeutic approaches or enhance diagnostic criteria.

### Evidence from Context
1. **Comparative Structures**: The tau filaments in CTE contain both 3R and 4R tau isoforms, similar to Alzheimer's disease but distinct from CBD, which only has 4R isoforms [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6)].
2. **Structural Similarity to CBD**: In both CBD and CTE, cryo-EM reveals that these protofilaments have additional core densities surrounded by the tau protein chain. The primary structural difference is the environment enclosing this density, which is positively charged in CBD [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p8)].
3. **Cryo-EM Structural Resolution**: High-resolution cryo-EM maps were obtained for tau filaments in CBD, providing detailed atomic models that could serve as a reference for understanding similar structures in CTE [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p8)].

### Treatment Suggestions
1. **Targeting Both 3R and 4R Tau Isoforms**: For potential therapeutic approaches targeting CTE, focusing on compounds that can disrupt both 3R and 4R tau polymerization may be appropriate. This aligns with the structural insights from CTE tau filament analysis that show a combination of these isoforms in their structure [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6)].

2. **Exploration of Positively Charged Environment Modulators**: Since CBD filaments in a positively charged environment offer a potential target, similar compounds could be explored for their effects on CTE if structural studies show analogous characteristics due to residue similarities in tau [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p8)].

3. **Use of High-Resolution Structural Data**: The detailed atomic models of tau filaments obtained from CBD can inform the design of small molecules or antibodies aimed at similar tau folds in CTE, allowing adaptation of strategies that effectively reach these structures [Novel tau filament fold in corticobasal degeneration (pmid_32050258_p8)].

### References
- Novel tau filament fold in corticobasal degeneration (pmid_32050258_p6). This document provides foundational insight into the structural makeup that differentiates CBD and CTE.
- Novel tau filament fold in corticobasal degeneration (pmid_32050258_p8). This reference outlines comparative structural details and resolution of tau filaments in CBD and its potential implications for similar tauopathies like CTE.

These pieces from the provided literature explore tau filament structures characteristic of CBD and partially address similar features in CTE, though further targeted cryo-EM studies specific to CTE would enhance the direct applicability of these insights.

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

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p2 ===

**`pmid_32050258_p2_t0_c0`** *(text)*

•  Dashboard •  Publications •  Account settings Log in [image] [image] Search PMC Full-Text Archive Search in PMC [image] •  Journal List •  User Guide •  [image] •  [image] •  [image] •  [image] [image] •  [image] •  [image] PERMALINK [image] Copy [image] As a library, NLM provides access to scientific literature. Inclusion in an NLM database does not imply endorsement of, or agreement with, the contents by NLM or the National Institutes of Health. Learn more: PMC Disclaimer | PMC Copyright Notice [image] Nature . Author manuscript; available in PMC: 2020 Aug 12. Published in final edited form as: Nature. 2020 Feb 12;580(7802):283–287. doi: 10.

**`pmid_32050258_p2_t1_c0`** *(text)*

1038/s41586-020-2043-0 •  Search in PMC •  Search in PubMed •  View in NLM Catalog •  Add to search Novel tau filament fold in

**`pmid_32050258_p2_t0_c1`** *(text)*

Inclusion in an NLM database does not imply endorsement of, or agreement with, the contents by NLM or the National Institutes of Health. Learn more: PMC Disclaimer | PMC Copyright Notice [image] Nature . Author manuscript; available in PMC: 2020 Aug 12. Published in final edited form as: Nature. 2020 Feb 12;580(7802):283–287. doi: 10.

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p3 ===

**`pmid_32050258_p3_t0_c0`** *(text)*

corticobasal degeneration Wenjuan Zhang Wenjuan Zhang 1MRC Laboratory of Molecular Biology, Cambridge, CB2 0QH, United Kingdom Find articles by Wenjuan Zhang 1, Airi Tarutani Airi Tarutani 2Department of Dementia and Higher Brain Function, Tokyo Metropolitan Institute of Medical Science, Tokyo, 156-8506, Japan. Find articles by Airi Tarutani 2, Kathy L Newell Kathy L Newell 3Department of Pathology and Laboratory Medicine, Indiana University School of Medicine, Indianapolis, IN 46202, USA Find articles by Kathy L Newell 3, Alexey G Murzin Alexey G Murzin 1MRC Laboratory of Molecular Biology, Cambridge, CB2 0QH, United Kingdom Find articles by Alexey G Murzin 1, Tomoyasu Matsubara Tomoyasu Matsubara 4Department of Neuropathology, Tokyo Metropolitan Institute of Gerontology, Tokyo, 173-0015, Japan.

**`pmid_32050258_p3_t1_c0`** *(text)*

Find articles by Tomoyasu Matsubara 4, Benjamin Falcon

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p4 ===

**`pmid_32050258_p4_t0_c0`** *(text)*

Benjamin Falcon 1MRC Laboratory of Molecular Biology, Cambridge, CB2 0QH, United Kingdom Find articles by Benjamin Falcon 1, Ruben Vidal Ruben Vidal 3Department of Pathology and Laboratory Medicine, Indiana University School of Medicine, Indianapolis, IN 46202, USA Find articles by Ruben Vidal 3, Holly J Garringer Holly J Garringer 3Department of Pathology and Laboratory Medicine, Indiana University School of Medicine, Indianapolis, IN 46202, USA Find articles by Holly J Garringer 3, Yang Shi Yang Shi 1MRC Laboratory of Molecular Biology, Cambridge, CB2 0QH, United Kingdom Find articles by Yang Shi 1, Takeshi Ikeuchi Takeshi Ikeuchi 5Department of Molecular Genetics, Brain Research Institute, Niigata University, Niigata 951-8585, Japan Find articles by Takeshi Ikeuchi 5, Shigeo Murayama Shigeo Murayama 4Department of Neuropathology, Tokyo Metropolitan Institute of Gerontology, Tokyo, 173-0015, Japan.

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

### === DOC pmid_32050258 / Novel tau filament fold in corticobasal degeneration. / pmid_32050258_p8 ===

**`pmid_32050258_p8_t0_c0`** *(text)*

and Gallyas-Braak silver (black) (f). Staining of frontal cortex from CBD cases 1–3 was negative when antibody RD3 (specific for 3R tau) was used (d). Nuclei were counterstained in blue. Scale bars, 50 μm. (g), Immunoblots using antibodies RD4, RD3 and AT8 of sarkosyl-insoluble tau extracted from the frontal cortex of CBD cases 1–3. (h), Negative-stain electron micrographs of Type I (narrow) and Type II (wide) tau filaments extracted from the frontal cortex of CBD case 1. Scale bar, 50 nm. We used cryo-EM and helical reconstruction in RELION (25) to determine the structures of both types of tau filaments of CBD (Figure 2a, Extended Data Figure 4, Extended Data Table 1). The ratios of Type II to Type I filaments ranged from 3:1 to 1:1, depending on cases (Extended Data Table 1). In the three cases, Type I filaments are composed of a single protofilament and adopt a novel four-layered fold. Like CTE filaments, each protofilament of CBD contains an additional density that is surrounded by density of the tau protein chain. Unlike CTE (19), the additional density is found in a positively charged environment. Type II filaments consist of pairs of identical protofilaments of Type I, related by C2 symmetry, with less well-resolved maps at the ends of the cores than in their central parts.

**`pmid_32050258_p8_t1_c0`** *(text)*

The maps showed side chain densities and β-strands that were well separated along the helical axis, allowing us to generate stereochemically refined atomic models (Figure 2b, Extended Data Figure 5e–h). Figure 2. Cryo-EM maps of CBD Type I and Type II tau filaments and atomic model of Type II filaments. [image] Open in a new tab (a), Cryo-EM maps of Type I tau filaments (upper panels) and Type II tau filaments (lower panels) from the frontal cortex of cases 1–3.

**`pmid_32050258_p8_t0_c1`** *(text)*

Like CTE filaments, each protofilament of CBD contains an additional density that is surrounded by density of the tau protein chain. Unlike CTE (19), the additional density is found in a positively charged environment. Type II filaments consist of pairs of identical protofilaments of Type I, related by C2 symmetry, with less well-resolved maps at the ends of the cores than in their central parts. For case 1, we obtained maps of Type I and Type II tau filaments at overall resolutions of 3.2 Å and 3.0 Å, respectively (Extended Data Figure 5a–d). Local resolution in the central part of Type II filaments extended to 2.8 Å.

**`pmid_32050258_p8_t1_c1`** *(text)*

Figure 2. Cryo-EM maps of CBD Type I and Type II tau filaments and atomic model of Type II filaments. [image] Open in a new tab (a), Cryo-EM maps of Type I tau filaments (upper panels) and Type II tau filaments (lower panels) from the frontal cortex of cases 1–3.

**`pmid_32050258_p8_t0_c2`** *(text)*

Type II filaments consist of pairs of identical protofilaments of Type I, related by C2 symmetry, with less well-resolved maps at the ends of the cores than in their central parts. For case 1, we obtained maps of Type I and Type II tau filaments at overall resolutions of 3.2 Å and 3.0 Å, respectively (Extended Data Figure 5a–d). Local resolution in the central part of Type II filaments extended to 2.8 Å.

