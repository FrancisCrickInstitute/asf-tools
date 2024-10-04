# Sample Sheet Processing in the current Demultiplexing pipeline
This pipeline manages the processing and transformation of Illumina samplesheets throughout multiple steps. These samplesheets, which contain critical metadata about samples, barcodes, and project information, are essential for correctly demultiplexing raw sequencing data and performing subsequent analysis. The handling of samplesheets in the pipeline is dynamic, allowing for validation, modifications, and error handling.
Before sample demultiplexing begins, the input Illumina samplesheet is checked and filtered by sample type to prevent downstream errors. Samples that do not adhere to the expected format are moved to a secondary samplesheet (using the `create_falseSS` process) during the initial validation. The remaining samples are then further categorized as either 10X or bulk samples. This initial data wrangling step ensures that the pipeline can process subsequent steps according to the specific requirements of each sample.
A detailed breakdown of each step follows.

## 1. **Samplesheet reformatting (`reformat_samplesheet`)**
The `reformat_samplesheet` function ensures that the provided sample sheet is properly formatted for downstream processing tools like `bcl2fastq` and `CellRanger`. Here’s how it works:

### Key Steps:
1. **Input validation:**
   - The expected input should follow an Illumina samplesheet format, which includes several subsections, such as: [Header], [Data] and any other software specific settings. Although V1 and V2 differ in the content of each subsection, the overall structure should remain the same for both. More information can be found [here]( https://help.connected.illumina.com/run-set-up/overview/sample-sheet-structure).
   - The sample sheet is read and filtered to only process information contained within the [Data] section of the Illumina pipeline, therefore temporarily ignoring other metadata.
-  Critical columns such as `Lane`, `Sample_ID`, `index`, `index2`, `Sample_Project`, `ReferenceGenome`, and `DataAnalysisType` are verified to be present.
   - Samples without valid index information (both `index` and `index2` must be strings) are identified and removed.
2. **iCLIP Lane collapsing:**
   - iCLIP samples are grouped by lane. If multiple iCLIP samples exist within the same lane, they are collapsed into one, preserving the minimum and maximum sample numbers for that lane.
   - The `Sample_ID` and `User_Sample_Name` are updated accordingly, with the `index` and `index2` values reset to empty for the merged sample.
- The new `Sample_ID` should have two integers added as a suffix to the original sample name to indicate the minimum and the maximum sample number.

3. **Handling 10X sequencing samples:**
   - At this point, 10X samples are separated from Bulk samples.
   - Specific subsets of 10X sample types (including `10X-ATAC`, `10X-DNA`, `10X-Arc`) are identified by extracting the value from the `[ DataAnalysisType]` field.
   - For each sample type, new, separate illumina samplesheets are created. Within the samplesheet, the reference genomes is updated by identifying the corresponding sample species (if the entry can be found within the `cellranger_ref_genome_dict` dictionary, then it would be updated with the matching value; otherwise the original value is left unchanged).

4. **Generating output:**
   - The main reformatted sample sheet, `ReformattedSampleSheet.csv`, is generated.
   - Additional files (`tenX_samplesheet.tenx.csv`, `tenX_samplesheet.ATACtenx.csv`, etc.) are created for 10X data, ensuring compatibility with CellRanger.
   - Empty rows or problematic rows are removed, ensuring that only valid samples proceed to sequencing.
-  A text file (`true.bcl2fastq.txt` or `false.bcl2fastq.txt`) is created to signal whether `bcl2fastq` is needed.
## 2. **Check samplesheet (`check_samplesheet`)**
1. **Identifying indexing type:**

   - Lanes with one samples are removed.
   -  Check for mixed indexing (single and dual index in the same lane). 
   - Fail if mixed indexing is found (ie. `samplesheet_check = "fail"`).
  - Check for index length consistency across lanes and for index length discrepancies within lanes
 - Write results (“pass” or “fail”) into a text file.

## 3. **Creating false samplesheet (`make_fake_SS`)**
The `create_falseSS.py` script is used to identify and remove problematic samples, particularly those with mismatched indexing configurations, across lanes. It generates a "false" sample sheet that only contains valid samples, with problematic ones logged separately. This step is only run is the process `check_samplesheet` returns a `fail.txt` file.

### Key Steps:
1. **Lane structure validation:**
   - The sample sheet is read and filtered to only process information contained within the [Data] section of the Illumina pipeline, therefore temporarily ignoring other metadata.
- The function first filters out lanes that only contain a single sample, typically associated with iCLIP experiments.
   - These lanes are ignored in further processing, as they do not require index length validation.

2. **Identifying indexing type:**
   - The function checks whether the samplesheet contains a mix of single and dual indexes:
     - Single-index samples are identified by the absence of an `index2` value.
     - Dual-index samples are identified when both `index` and `index2` are present.
   - New columns (`index1_len` and `index2_len`) are added to track the lengths of the indexes.

3. **Lane-specific index length validation:**
   - For each lane, the function calculates the maximum index length. All samples in the lane are then compared against this maximum:
     - Single-index samples in dual-index lanes are flagged as problematic.
     - Samples with index lengths shorter than the maximum in their lane are also flagged.
   - Samples with indexing issues are dropped from the final samplesheet, and their indices are logged in the `problem_samples_list.txt` file.
   - If all samples in the sheet are deemed problematic, the pipeline exits with an error message indicating an empty sample sheet.

5. **Generating output:**
   - The remaining valid samples are saved into a new file, `fake_samplesheet.csv`.
   - A list of problematic sample indices is saved into `problem_samples_list.txt`.

## 4. **Separation of Bulk, 10X and problematic samples processing**
At this stage in the pipeline, the processing of bulk, 10X, and problematic samples diverges into distinct paths:

- **Bulk Samples**: These samples are directed to the `bcl2fastq_default` process.
  
- **Problematic Samples**: Samples identified as problematic (i.e., those listed in `fake_samplesheet.csv` that return a `fail` during the `check_samplesheet` step) are processed through the following steps:
  - `bcl2fastq_problem_SS`
  - `parse_jsonfile`
  - `recheck_samplesheet`
  
- **10X Samples**: These samples proceed to the following processes:
  - `cellRangerMkFastQ`
  - `cellRangerMoveFqs`
  - `cellRangerCount`

The samplesheets of Bulk and 10X samples aren't edited any further.

## 5. **Further sample processing (`bcl2fastq_problem_SS`, `parse_jsonfile`, `recheck_samplesheet`)**
- The `false_samplesheet.csv` file, which contains only samples that passed all checks at the `make_fake_SS` step, is processed through a bcl2fastq command to generate FASTQ files. The resulting `.json` output file from this bcl2fastq run is used to identify unknown barcodes.
- The `parse_json.py` script extracts these unknown barcodes and scans the sample sheet for problematic samples whose indices match the unknown barcodes. If a match is found, the index will be replaced with the value of the unknown barcode and generate a new, updated samplesheet. This enables the pipeline to better handle scenarios where a single index is used in a dual-indexed lane.
- Lastly, the new sample sheet undergoes a final check to ensure consistency with the original sheet, specifically verifying that fields like "Sample_ID" and "Lane" match. Additionally, it confirms that index values have been updated correctly. If any index fields return a “NAN” or “None” value, this process will generate a `fail.txt` file. The generation of a `pass.txt` file would enable the previously problematic samples to move forward in the pipeline, ie. to proceed to the `bcl2fastq_default` process.