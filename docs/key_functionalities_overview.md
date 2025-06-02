# General parameters/values
## Modes
- __DataTypeMode__ is in `io/data_management.py`. Useful when selecting between GENERAL, ONT or ILLUMINA mode.
- __DeleteMode__ is in `io/utils.py`. Useful for the `delete_all_items` function. Can be used to either select all files in a directory, or the directory tree.
- __IndexMode__ is in `illumina/illumina_utils.py`. Useful for the process_sample_sheet function.

## Run ID
- __ONT__: can be extracted from the folder name
- __Illumina__: needs to be extracted from the `flowcell` value in the `RunInfo.xml` file

## Broad functionalities
- __check_file_exist__ is in `io/utils.py`. Can be used to check for the presence of a file matching a specific pattern in its file name.
- __get_pipeline_params__ is in `api/clarity/clarity_helper_lims.py`. It enables the extraction of information from specific or custom fields, with each parameter being split by a `;` character. It splits the parameter name from the parameter value using a custom sep value. This function is also used in in `nextflow/gen_demux_run.py` within the `extract_pipeline_params` function, where it is called with the separator hardcoded as `=`. For the input to be processed correctly, the field value should look like this: *parameter_1 = value1; parameter_2 = 2*.

# API notes
- __clarity_lims.py__ <br>
Connects directly to the Clarity API.
Has minimal filtering/processing of the output.

- __clarity_helper_lims.py__ <br>
    Builds on top of the _clarity_lims_ functionalities. <br>

    When we only have the `run_id` value, we can run:
    - get_sample_barcode_from_runid
    - get_sample_custom_barcode_from_runid
    - collect_sample_info_from_runid (no barcode info)
    - collect_samplesheet_info (barcode info included)

# Illumina notes
__Run ID__ can be extracted in 2 ways, depending on the input:
- _RunInfo.xml_ file -> `extract_illumina_runid_fromxml` function in `illumina/illumina_utils.py`
- _path_ to the raw data -> `extract_illumina_runid_frompath` function, also in `illumina/illumina_utils.py`
__BCL Convert__ related functionalities
- _`generate_overridecycle_string`_ -> function in `illumina/illumina_utils.py`, useful when index length is smaller than specified in the RunInfo.xml file. Assumes that: index_length < runinfo_specified_length.

# Running pipelines
- __main.py__ <br>
    Main code for the interactive CLI functionality. <br>
    Current commands are:
    - gen_demux_run
    - deliver_to_targets
    - scan_run_state

- __io/data_management.py__ <br>
    The __Data Management__ class allows us to:
    1) check if the sequencing on the instrument is complete for each run
    2) check if the pipeline (post-sequencing) is complete
    3) check if the results have been delivered
    4) deliver data to scientists
    5) delete non-essential files from old dirs
    <br>

    expanding on the points above:
    1) 2 separate functions, one for ONT, one for Illumina
    2) looks for this file _results/pipeline_info/workflow_complete.txt_
    3) no notes
    4) no notes
    5) - any mode: deletes the work folder and all its contents
        - ONT -> **not** demultiplexed (ie. only 1 sample) -> deletes all the contents inside the _results/dorado/_ folder (not the folder itself) + deletes work folder
    - `scan_run_state` merges the functionalities mentioned above in point 1,2 and 3


