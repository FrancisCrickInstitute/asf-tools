# Design considerations

The pipeline is designed to split Bulk samples from 10X samples prior to running `bcl2fastq`. While both `bcl2fastq` and `cellranger mkfastq` convert BCL files into FASTQ files and could process 10X samples, all 10X samples are processed using the cellranger command. 
There are a few good reasons for doing so:
- Using `cellranger mkfastq` ensures compatibility with other cellranger tools, particularly `cellranger count`, making the pipeline more seamless and less error-prone.
- `cellranger mkfastq` is optimized to automatically recognize and process the 10x Genomics-specific structure of BCL files, which reduces manual configuration. 
- `cellranger mkfastq` is specifically designed to handle the unique barcode structure used in 10x Genomics assays, which often involve dual-indexing and other custom sequencing configurations. While `bcl2fastq` can also demultiplex data, it may require more complex configuration to correctly handle 10x' custom barcodes.