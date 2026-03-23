# Question

What is the role of PLA2G15 as a BMP hydrolase in lysosomes?

**Vectors:** `data/real_vectors.jsonl` | topk=5, rerank=True, topn=50

---

## Answer

The role of PLA2G15 as a BMP hydrolase in lysosomes is a significant discovery in understanding lipid metabolism and its related pathologies. Bis(monoacylglycero)phosphate (BMP) is a lipid present within lysosomal vesicles, critical for lysosomal lipid metabolism, and its imbalance is a marker in various lysosome-associated diseases, including some neurodegenerative and cardiovascular diseases. BMP is structurally unique, and this structural uniqueness confers resistance to hydrolysis in lysosomes, thereby regulating its metabolic function [PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease (pmid_40335701_p1)].

PLA2G15, identified as a physiological BMP hydrolase, plays a crucial role by mediating the turnover of BMP within lysosomes. The accumulation of BMP species in lysosomal disorders is reversible by the administration of wild-type PLA2G15, highlighting its therapeutic potential. Moreover, targeting PLA2G15 was shown to ameliorate disease pathologies in diseases such as Niemann–Pick disease type C1 by reducing cholesterol accumulation and thus extending lifespan in model organisms [PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease (pmid_40335701_p1)].

1. **Therapeutic Targeting of PLA2G15**: Considering the role of PLA2G15 in BMP turnover, therapies aimed at enhancing or mimicking its activity could be beneficial in lysosomal storage diseases characterized by BMP accumulation, such as Niemann–Pick disease type C1. However, the consideration of specific lysosomal disorders and the genetic background of patients is crucial before applying such therapies [PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease (pmid_40335701_p1)].

2. **PLA2G15 in Lipid Metabolism Disorders**: Intervention strategies, including gene therapy to restore PLA2G15 function or small molecules that activate PLA2G15, might provide benefits in metabolic disorders where lysosomal lipid breakdown is impaired. Therapeutic targeting of PLA2G15 should be considered carefully in individuals with intact BMP metabolism to avoid unintended lipid dysregulation [PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease (pmid_40335701_p1)].

3. **Research on BMP Isomers and Hydrolysis Resistance**: Further research into synthesizing and testing BMP stereoisomers might provide insights into more selective therapeutic targets for diseases involving lysosomal dysfunction. Careful monitoring of hydrolysis resistance is necessary when developing therapies that modify PLA2G15 activity, especially in synthetically altered BMP environments [PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease (pmid_40335701_p1)].

References:
- PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease (pmid_40335701_p1): Provides evidence for the role of PLA2G15 in BMP turnover and its therapeutic potential.


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

### === DOC pmid_40335701 / PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease. / pmid_40335701_p1 ===

**`pmid_40335701_p1_fig_0_c0`** *(image)*

![page_1_fig_0.png](../data/raw/pmid_40335701/page_1_fig_0.png)

**`pmid_40335701_p1_t0_c0`** *(text)*

474  |  Nature  |  Vol 642  |  12 June 2025 Article PLA2G15 is a BMP hydrolase and its targeting ameliorates lysosomal disease Kwamina Nyame1,2,3,4,10, Jian Xiong1,2,3,10, Hisham N. Alsohybe1,2,3, Arthur P. H. de Jong5, Isabelle V. Peña1,2,3, Ricardo de Miguel6, Thijn R. Brummelkamp5,7, Guido Hartmann5, Sebastian M. B. Nijman5, Matthijs Raaben5, Judith A. Simcox8, Vincent A. Blomen5 & Monther Abu-Remaileh1,2,3,9 ✉ Lysosomes catabolize lipids and other biological molecules, maintaining cellular and organismal homeostasis. Bis(monoacylglycero)phosphate (BMP), a major lipid constituent of intralysosomal vesicles, stimulates lipid-degrading enzymes and is altered in various human conditions, including neurodegenerative diseases1,2. Although lysosomal BMP synthase was recently discovered3, the enzymes mediating BMP turnover remain elusive. Here we show that lysosomal phospholipase PLA2G15 is a physiological BMP hydrolase. We further demonstrate that the resistance of BMP to lysosomal hydrolysis arises from its unique sn2, sn2′ esterification position and stereochemistry, as neither feature alone confers resistance. Purified PLA2G15 catabolizes most BMP species derived from cell and tissue lysosomes.

**`pmid_40335701_p1_t1_c0`** *(text)*

Consistent with our biochemical data, PLA2G15-deficient cells and tissues accumulate several BMP species, a phenotype reversible by supplementing wild-type PLA2G15 but not its inactive mutant. Targeting PLA2G15 reduces the cholesterol accumulation in fibroblasts of patients with Niemann–Pick disease type C1 and significantly ameliorates disease pathologies in Niemann–Pick disease type C1-deficient mice, leading to an extended lifespan. Our findings established the rules governing BMP stability in lysosomes and identified PLA2G15 as a lysosomal BMP hydrolase and a potential target for therapeutic intervention in neurodegenerative diseases. Lysosomes are vital for cellular waste removal, nutrient recycling and maintaining homeostasis, particularly by breaking down complex lipids using hydrolytic enzymes. Lipid degradation within lysosomes is facilitated by intralysosomal vesicles rich in a unique lipid called bis(monoacylglycero)phosphate (BMP)1. BMP significantly enhances lysosomal lipid metabolism, and its imbalance is a hallmark of various lysosome-associated diseases, including age-related neurodegen- eration, viral infection, cancer and atherosclerotic cardiovascular disease1–3.

**`pmid_40335701_p1_t2_c0`** *(text)*

BMP is a structural isomer of phosphatidylglycerol with symmetrical acyl chain positions on the two glycerol moieties and a unique S,S ste- reoconfiguration1,2 (Fig. 1a). Partial deacylation of these phospholipids generates one fatty acid and lysophosphatidylglycerol (LPG) (Fig. 1b), whereas its complete deacylation releases two fatty acids and glycer- ophosphorylglycerol (GPG)5–7 (Fig. 1c). BMP is stable in the lysosomal environment. However, the rules that govern BMP catabolism remain unclear. Some reports speculate that its unique stereochemistry may confer resistance to its degradation by lysosomal hydrolases, a necessity for its proposed function in stimulating lipid degradation in the lysosome8, whereas others indicate that BMP is susceptible to enzyme-mediated hydrolysis5,6,9–13. Because of its therapeutic potential, understanding BMP turnover and uncovering its physiological hydro- lases in the lysosome are of great interest. Here we show that the unique sn2, sn2′ position of the acyl chains of BMP is required to protect S,S BMPs from lysosomal hydrolysis by the abundant lysosomal phospholi- pase A2 (PLA2G15), which we establish as a BMP hydrolase in addition to its role as a general acid phospholipase B.

**`pmid_40335701_p1_t3_c0`** *(text)*

2Department of Genetics, Stanford University, Stanford, CA, USA. 3Institute for Chemistry, Engineering and Medicine for Human Health (Sarafan ChEM-H), Stanford University, Stanford, CA, USA. 4Department of Biochemistry, Stanford University, Stanford, CA, USA. 5Scenic Biotech, Science Park 301, Amsterdam, The Netherlands. 6Pathology Department, AnaPath Services GmbH, Liestal, Switzerland. 7Oncode Institute, Division of Biochemistry, The Netherlands Cancer Institute, Amsterdam, The Netherlands. 8Howard Hughes Medical Institute, Department of Biochemistry, University of Wisconsin–Madison, Madison, WI, USA. 9The Phil & Penny Knight Initiative for Brain Resilience at the Wu Tsai Neurosciences Institute, Stanford University, Stanford, CA, USA. 10These authors contributed equally: Kwamina Nyame, Jian Xiong. ✉e-mail: monther@stanford.

**`pmid_40335701_p1_t4_c0`** *(text)*

edu

**`pmid_40335701_p1_t0_c1`** *(text)*

Here we show that lysosomal phospholipase PLA2G15 is a physiological BMP hydrolase. We further demonstrate that the resistance of BMP to lysosomal hydrolysis arises from its unique sn2, sn2′ esterification position and stereochemistry, as neither feature alone confers resistance. Purified PLA2G15 catabolizes most BMP species derived from cell and tissue lysosomes. Furthermore, PLA2G15 efficiently hydrolyses synthesized BMP stereoisomers with primary esters, challenging the long-held thought that BMP stereochemistry alone ensures resistance to acid phospholipases. Conversely, BMP with secondary esters and S,S stereoconfiguration is stable in vitro and requires acyl migration for hydrolysis in lysosomes.

**`pmid_40335701_p1_t1_c1`** *(text)*

Lipid degradation within lysosomes is facilitated by intralysosomal vesicles rich in a unique lipid called bis(monoacylglycero)phosphate (BMP)1. BMP significantly enhances lysosomal lipid metabolism, and its imbalance is a hallmark of various lysosome-associated diseases, including age-related neurodegen- eration, viral infection, cancer and atherosclerotic cardiovascular disease1–3. Although we recently identified the lysosomal BMP synthase3, which was then validated as the sole lysosomal BMP synthase in cells by another group that also identified potential circulating machineries that might make BMP4, many questions about BMP degradation remain.

**`pmid_40335701_p1_t2_c1`** *(text)*

Because of its therapeutic potential, understanding BMP turnover and uncovering its physiological hydro- lases in the lysosome are of great interest. Here we show that the unique sn2, sn2′ position of the acyl chains of BMP is required to protect S,S BMPs from lysosomal hydrolysis by the abundant lysosomal phospholi- pase A2 (PLA2G15), which we establish as a BMP hydrolase in addition to its role as a general acid phospholipase B. In a parallel genetic screening effort, we identified PLA2G15 as a modifier of cholesterol staining and https://doi.org/10.1038/s41586-025-08942-y Received: 17 May 2024 Accepted: 25 March 2025 Published online: 7 May 2025 Open access Check for updates 1Department of Chemical Engineering, Stanford University, Stanford, CA, USA.

**`pmid_40335701_p1_t3_c1`** *(text)*

8Howard Hughes Medical Institute, Department of Biochemistry, University of Wisconsin–Madison, Madison, WI, USA. 9The Phil & Penny Knight Initiative for Brain Resilience at the Wu Tsai Neurosciences Institute, Stanford University, Stanford, CA, USA. 10These authors contributed equally: Kwamina Nyame, Jian Xiong. ✉e-mail: monther@stanford.

**`pmid_40335701_p1_t0_c2`** *(text)*

Purified PLA2G15 catabolizes most BMP species derived from cell and tissue lysosomes. Furthermore, PLA2G15 efficiently hydrolyses synthesized BMP stereoisomers with primary esters, challenging the long-held thought that BMP stereochemistry alone ensures resistance to acid phospholipases. Conversely, BMP with secondary esters and S,S stereoconfiguration is stable in vitro and requires acyl migration for hydrolysis in lysosomes.

**`pmid_40335701_p1_t1_c2`** *(text)*

BMP significantly enhances lysosomal lipid metabolism, and its imbalance is a hallmark of various lysosome-associated diseases, including age-related neurodegen- eration, viral infection, cancer and atherosclerotic cardiovascular disease1–3. Although we recently identified the lysosomal BMP synthase3, which was then validated as the sole lysosomal BMP synthase in cells by another group that also identified potential circulating machineries that might make BMP4, many questions about BMP degradation remain.

**`pmid_40335701_p1_t2_c2`** *(text)*

Here we show that the unique sn2, sn2′ position of the acyl chains of BMP is required to protect S,S BMPs from lysosomal hydrolysis by the abundant lysosomal phospholi- pase A2 (PLA2G15), which we establish as a BMP hydrolase in addition to its role as a general acid phospholipase B. In a parallel genetic screening effort, we identified PLA2G15 as a modifier of cholesterol staining and https://doi.org/10.1038/s41586-025-08942-y Received: 17 May 2024 Accepted: 25 March 2025 Published online: 7 May 2025 Open access Check for updates 1Department of Chemical Engineering, Stanford University, Stanford, CA, USA.

