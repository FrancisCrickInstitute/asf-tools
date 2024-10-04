# Illumina samplesheet processing in the Demultiplexing pipeline
The Demultiplexing pipeline extracts information about samples and their corresponding runs from both Clarity and the `RunInfo.xml` file. This information is essential for creating an Illumina-compliant samplesheet. For more details on how this samplesheet is created, please refer to the file `illumina_samplesheet_perl.md`.

Before demultiplexing can occur, additional data wrangling is required. The main steps involve:

1. **Validation**: verifying the accuracy and completeness of the inputted information.
2. **Sample Splitting**: categorizing samples based on their type - whether they are Bulk, 10X, or classified as “problematic” (i.e., samples that fail validation checks).

Once samples have been categorized, they will be processed accordingly and eventually demultiplexed. For further information on the data wrangling process, please consult the file `illumina_samplesheet_nextflow_old_demux.md`.

For a more comprehensive overview of the entire demultiplexing pipeline, refer to the graph in `illumina_old_demux_overview.png`.
