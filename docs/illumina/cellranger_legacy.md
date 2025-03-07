# Cellranger Notes

1. **Supported Data/Analysis Types**
2. **Current Software Usage**
3. **Do we need to run different Cellranger types?**
4. **Can the latest version of Cellranger handle ATAC projects too?**
5. **In summary: do we need to run different Cellranger types?**
6. **What software do we need to run to get the data ready for Cellranger?** (e.g., mkfastq, bcl2fastq, bcl convert)
7. **What follow-up software do we need to use?** (cellranger count, fastqc, fastq screen, multiqc)
8. **Guideline on parameters/commands to be used.**
9. **Other notes.**
10. **Alternative Options**


## 1. Supported Data/Analysis Types
The following data and analysis types are currently supported by Cellranger:
- **10X 3' Gene Expression**
- **10X GEX**
- **10X CNV**
- **10X ATAC**
- **10X Multiomics ATAC**
- **10X Arc**
- **10X 3' Nuclei**

## 2. Current Software Usage
We are currently utilizing the following Cellranger applications based on the specific data analysis needs of our samples:
- **Cellranger:** General usage for single-cell RNA-seq.
- **Cellranger ATAC:** For ATAC-seq projects.
- **Cellranger DNA:** For DNA analysis (note: this is being phased out).
- **Cellranger Arc:** For multiomic analyses.

The `Cellranger mkfastq` utility serves a broader purpose in preparing fastq files.
Other specific applications such as `cellranger count`, `cellranger-dna CNV`, and `cellranger-atac count` are selected based on the sample type.  
10X-Arc data are currently being processed by Cellranger-arc mkfastq, but no follow up _cellranger-arc_ or _cellranger-arc count_. Instead, samples are processed in two separate steps, once with standard `cellranger` (it looks for the data type 10X-Multiomics-GEX) and once with `cellranger-atac` (it looks for the data type 10X-Multiomics-ATAC).

## 3. Do We Need Different Cellranger Types?
Yes, for now.   

Currently, the kits for **Cellranger DNA** have been discontinued, eliminating the need for its inclusion in our new pipeline. However, we will still need to run the following:
- **Standard Cellranger** (potentially upgraded to the latest version 8.0)
  - 10X-3prime
  - 10X-3prime-nuclei
  - 10X-Multiomics-GEX
- **CellRanger ATAC**
   - 10X-ATAC
   - 10X-Multiomics-ATAC
- 10X-Arc

Additionally, we will need to incorporate **Cellranger Multi** and **Cellranger VDJ** as alternatives to the **Cellranger Count** into our new pipeline.

## 4. Can the standard CellRanger handle ATAC Projects?
"Cellranger provides a comprehensive suite of analysis pipelines designed for 10X Genomics Chromium single-cell data, which includes sample demultiplexing, barcode processing, gene counting, and feature barcode analysis." cit. [Cellranger Documentation](https://github.com/10XGenomics/cellranger?tab=readme-ov-file).
It appears that **ATAC projects** are currently not explicitly supported in the latest version. 
However, the latest update was designed to handle NovaSeqX data types better. The current advice for the processing of new ATAC projects is to use run standard _CellRanger_ for demultiplexing, followed by _cellranger-atac_. This is different from legacy since _cellranger-atac_ is not used for both demultiplexing and count. The Cellranger developers have expressed no interest in updating the _cellranger-atac_ pipeline aat any time soon. For more information, click [here](https://kb.10xgenomics.com/hc/en-us/articles/26367321866125-How-do-I-generate-single-cell-ATAC-or-multiome-ATAC-FASTQ-files-from-NextSeq-or-NovaSeq-X) 


## 5. Software Required prior to CellRanger run
To prepare the data for Cellranger, the following tool is necessary:
- **bcl convert:** all data types can now be processed using this software

**Cellranger Mkfastq** functionality is included in _bcl convert_, therefore all data analysis types can now be processed using only _bcl convert_. Switching to a single software for all data analysis type should make long term maintanance (eg. upgrades) easier to manage.

## 6. Follow-Up Software
After running Cellranger, it is recommend to use the following software for further data analysis:
- **Cellranger count** for counting reads and generating gene expression matrices.
- **Cellranger multi** 
- **Cellranger vdj** 
- **FastQC:** for assessing the quality of sequencing data.
- **Fastq Screen:** to check for contamination in fastq files.
- **MultiQC:** for aggregating and visualizing multiple quality control reports.

## 7. Parameters and Command Guidelines
### Data analysis value
The appropriate type of Cellranger to run can be determined from the "data analysis type" column in the original samplesheet (or the v2 Illumina samplesheet, if included), or from the suffix in the sample names (_not_ in the sample limsID).

While the "data analysis type" column usually provides the correct value for most projects, it may not always accurately capture certain edge cases, such as VDJ (which is currently processed as a standard gene expression (GE) run). This approach has worked so far since the Genomics team only required the output from the count for QC purposes. However, transitioning to a more tailored approach may warrant the use of a more appropriate Cellranger option (between count, multi and vdj) to better meet future needs.

Meanwhile, the sample name suffix can be used to reliably identify the analysis type. These values are also used by the colleagues in charge of the library prep within Genomics.

Currently used suffixes:
- GEX: Gene expression (3' or 5')
- snGEX: Gene expression (3' or 5'), where input sample was single nuclei
- mxGEX: Multiomics GEX
- fxGEX: fixed cell GEX
- ATAC: ATAC library
- mxATAC: Multiomics ATAC
- TCR: T cell receptor
- BCR: B cell receptor
- ADT: TotalSeqA, Citeseq (Antibody-derived tag)
- HTO: TotalSeqA, Hashing (Hash tag oligo)
- TSB: TotalSeqB (Feature Barcoding)
- TSC: TotalSeqC (Feature Barcoding)
- fxTSC: fixed cell TotalSeqC
- CRISPR: CRISPR screening library
- CMO: Cell Multiplex Oligo (CellPlex)
- BEAM: Barcode Enabled Antigen Mapping

Retired suffixes, not used any more:
- FB: Feature Barcoding
- TSA: TotalSeq A
- CITE: another name for ADT - stands for Cellular Indexing of the Transcriptome and Epitopes by Sequencing
- VDJ: Either TCR or BCR
- CSP: Cell surface protein

What they mean:
- GEX: normal cell ranger count
- snGEX: normal cell ranger count with introns included
- mxGEX: cellranger count with --chemistry=ARC-v
- TCR or BCR: cellranger VDJ
- fxGEX: cellranger-multi
- ATAC: cellranger-atac
- mxATAC: cellranger-atac with --chemistry=ARC-v1
- anything else: **no** cellranger run


## 8. Other Notes
Since NovaSeqX ATAC need to be initially demultiplexed using the latest version of the cellranger software, these also need to be processed using BCL Convert. More information can be found [here](https://kb.10xgenomics.com/hc/en-us/articles/26367321866125-How-do-I-generate-single-cell-ATAC-or-multiome-ATAC-FASTQ-files-from-NextSeq-or-NovaSeq-X).


### Graph overview


## 9. Alternative Options
Should we consider using [`https://github.com/nf-core/demultiplex/`](https://github.com/nf-core/demultiplex/) as an alternative for demultiplexing and preprocessing?
