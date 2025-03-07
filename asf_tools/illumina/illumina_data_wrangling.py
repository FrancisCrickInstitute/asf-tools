import json
import logging
import os
import warnings

from asf_tools.illumina.illumina_utils import (
    atac_reformat_barcode,
    dlp_barcode_data_to_dict,
    extract_cycle_fromxml,
    extract_illumina_runid_fromxml,
    filter_readinfo,
    filter_runinfo,
    generate_bcl_samplesheet,
    generate_bclconfig,
    generate_overridecycle_string,
    group_samples_by_index_length,
    runinfo_xml_to_dict,
    split_by_project_type,
)


log = logging.getLogger(__name__)

SINGLE_CELL_PROJECT_TYPES = [
    "Single Cell",
    "10X",
    "10x Multiomics",
    "10x multiome",
    "10X-3prime-nuclei",
    "10X-Multiomics-GEX",
    "10X-FeatureBarcoding",
]
SINGLE_CELL_DATA_ANALYSIS_TYPES = [
    "10X-3prime",
    "10X-CNV",
    "10X-FeatureBarcoding",
    "10X-Multiomics",
    "10X-Multiomics-GEX",
    "10X-Flex",
]
ATAC_PROJECT_TYPES = ["10X ATAC", "10X Multiomics ATAC", "10X-Multiomics-ATAC"]  # do not include bulk samples, so no matches to "ATAC" or "ATAC-Seq"
ATAC_DATA_ANALYSIS_TYPES = [
    "10X-ATAC",
]

SINGLE_CELL_PROJECT = SINGLE_CELL_PROJECT_TYPES + SINGLE_CELL_DATA_ANALYSIS_TYPES
ATAC_SC_PROJECT = ATAC_PROJECT_TYPES + ATAC_DATA_ANALYSIS_TYPES
DLP_PROJECT = ["DLP", "DLPplus"]


def generate_illumina_demux_samplesheets(clarity_lims, runinfo_path, output_path, bcl_config_path=None, dlp_sample_file=None):
    """
    Generate Illumina demultiplexing samplesheets.

    This function is divided into two main sections:
    1. Gathering and formatting sample information as required for further processing.
    2. Gathering BCL Convert specific information.

    The first part of this function performs the following steps:
    1. Extract RunID value (Flowcell ID) from the RunInfo.xml file.
    2. Extract Cycle length value (NumCycles) from the RunInfo.xml file.
    3. Use the RunID value to generate a dictionary of dictionaries (`samples_all_info`) with this information for each sample:
        sample_name (str): {
            "group": lab (str),
            "user": user_fullname (str),
            "project_id": project_id (str),
            "project_type": project_type (str or None),
            "reference_genome": reference_genome (str or None),
            "data_analysis_type": data_analysis_type (str or None),
            "barcode": reagent_barcode (str)
        }
    4. Extract information from `samples_all_info` and format it as required by the `BCLConvert_Data` section of the final samplesheets, including:
        - Filtering `samples_all_info` to only keep the "sample_name" and "barcode" information.
        - Reformatting "barcode" value and assigning it to "index" (and "index2" where appropriate).
        - Saving the formatted information in `sample_and_index_dict`.
    5. Evaluate Index length for each sample and group them based on the index length value. The groups and associated samples are saved in the `split_samples_by_indexlength` list.
    6. Create a subset of `sample_and_index_dict` for each group listed in `split_samples_by_indexlength`.
    7. If the Cycle length does not match the Index length, calculate the new OverrideCycle value.

    The second part of this function performs the following steps:
    1. Load RunInfo.xml file and filter out unnecessary information.
    2. If no BCL Config file is provided, generate a basic config file with relevant information.
    3. Extract information from the BCL Config file if provided.
    4. Obtain read specific information and format it as required by BCL Convert.
    5. Subdivide samples into different workflows based on project type.
    6. Generate samplesheets for each workflow (DLP, single cell, ATAC, and other samples - aka bulk samples).

    Parameters:
    cl (object): An object that provides methods to collect samplesheet information.
    runinfo_path (str): Path to the RunInfo.xml file.
    output_path (str): Path to the output directory where samplesheets will be saved.
    bcl_config_path (str, optional): Path to the BCL Config file. If not provided, a basic config file will be generated.
    dlp_sample_file (str, optional): Path to the DLP sample file.

    Returns:
    None
    """
    # Obtain sample information and format it as required by `BCLConvert_Data`
    flowcell_id = extract_illumina_runid_fromxml(runinfo_path)
    samples_all_info = clarity_lims.collect_samplesheet_info(flowcell_id)

    # Load RunInfo.xml file and filter out unnecessary information
    run_info_dict = runinfo_xml_to_dict(runinfo_path)
    run_info_dict_filt = filter_runinfo(run_info_dict)

    # If no BCL Config file is provided, generate a basic config file with relevant information
    if not bcl_config_path:
        # Generate config json
        machine_type = run_info_dict_filt["machine"]
        config_json = generate_bclconfig(machine_type, flowcell_id)

        # Save the config json to a file
        bcl_config_path = os.path.join(output_path, "bcl_config_" + flowcell_id + ".json")
        with open(bcl_config_path, "w") as file:
            json.dump(config_json, file, indent=4)
    else:
        # Extract info from the BCL Config file
        with open(bcl_config_path, "r") as file:
            config_json = json.load(file)

    header_dict = config_json["Header"]
    bcl_settings_dict = config_json["BCLConvert_Settings"]

    # Obtain read specific information and format it as required by BCLconvert
    read_info_dict = runinfo_xml_to_dict(runinfo_path)
    read_info_dict_filt = filter_readinfo(read_info_dict)
    reads_list = read_info_dict_filt["reads"]

    # Convert to dictionary
    reads_dict = {item["read"]: item["num_cycles"] for item in reads_list}
    key_replacements = {
        "Read 1": "Read1Cycles",
        "Index 2": "Index1Cycles",
        "Index 3": "Index2Cycles",
        "Read 4": "Read2Cycles",
    }
    reformatted_reads_dict = {
        key_replacements.get(key, key): value for key, value in reads_dict.items()  # Replace key if in key_replacements; otherwise, keep it
    }

    # Split samples into different workflows based on project type
    samples_categories_dict = {"single_cell": SINGLE_CELL_PROJECT, "atac": ATAC_SC_PROJECT, "dlp": DLP_PROJECT}
    categorised_sample_dict = split_by_project_type(samples_all_info, samples_categories_dict)
    # print(categorised_sample_dict)

    if "all_samples" in categorised_sample_dict.keys():
        # Set up variables required for the samplesheet generation
        samplesheet_name = f"{flowcell_id}_samplesheet"
        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
        generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, categorised_sample_dict["all_samples"], samplesheet_path)

    # Initiate processing only if samples are present for each workflow
    if "dlp" in categorised_sample_dict.keys() and categorised_sample_dict["dlp"]:
        filtered_dlp_samples = {}
        for sample in categorised_sample_dict["dlp"]:
            data_dict = dlp_barcode_data_to_dict(dlp_sample_file, sample)
            filtered_dlp_samples.update(data_dict)

        # Generate samplesheet with the updated settings
        samplesheet_name = samplesheet_name + "_dlp"
        samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
        generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, filtered_dlp_samples, samplesheet_path)

    # This should include 10X/single cell data
    if "single_cell" in categorised_sample_dict.keys() and categorised_sample_dict["single_cell"]:
        # print(categorised_sample_dict["single_cell"].items())
        # All samples are expected to be dual index and one index length
        samplesheet_name_sc = samplesheet_name + "_singlecell"

        # split samples into multiple entries based on lane values
        split_samples_dict = {}
        for sample, details in categorised_sample_dict["single_cell"].items():
            lanes = details["Lane"]  # Get the list of lanes
            for lane in lanes:
                # Create a new key for each unique (sample, lane) combination
                unique_key = f"{sample}_Lane_{lane}"
                # Copy the sample details and replace the Lane value with the current lane
                split_samples_dict[unique_key] = {**details, "Lane": lane}

        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name_sc + ".csv")
        generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, split_samples_dict, samplesheet_path)

    # This should include ATAC data
    if "atac" in categorised_sample_dict.keys() and categorised_sample_dict["atac"]:
        print(categorised_sample_dict["atac"])
        # All samples are expected to be single index and one index length
        samplesheet_name_atac = samplesheet_name + "_atac"

        # Subset sample_all_info to include only keys present in atac_sample
        # atac_all_sample_info = {key: samples_all_info[key["Sample_ID"]] for key in categorised_sample_dict["atac"] if key["Sample_ID"] in samples_all_info}
        atac_all_sample_info = {
            entry["Sample_ID"]: samples_all_info[entry["Sample_ID"]]
            for key, entry in categorised_sample_dict["atac"].items()
            if entry["Sample_ID"] in samples_all_info
        }
        print(atac_all_sample_info)
        new_atac_barcode_info = atac_reformat_barcode(atac_all_sample_info)

        # Format information according to BCL Convert requirements
        atac_samples_bcldata_dict = {}
        for sample in new_atac_barcode_info:
            # Iterate over each lane and each index for the current sample
            for lane in atac_all_sample_info[sample]["lanes"]:
                for barcode in new_atac_barcode_info[sample]["index"]:
                    # Create a unique entry for each lane-barcode combination
                    atac_samples_bcldata_dict[f"{sample}_L{lane}_{barcode}"] = {"Lane": lane, "Sample_ID": sample, "index": barcode, "index2": ""}

        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name_atac + ".csv")
        generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, atac_samples_bcldata_dict, samplesheet_path)

    if "other_samples" in categorised_sample_dict.keys() and categorised_sample_dict["other_samples"]:
        # print(categorised_sample_dict["other_samples"])
        split_samples_by_indexlength = group_samples_by_index_length(categorised_sample_dict["other_samples"])
        if len(split_samples_by_indexlength) == 0:
            warnings.warn("None of the bulk or 'other samples' have index information", UserWarning)

        if len(split_samples_by_indexlength) > 0:
            for index_length_sample_list in split_samples_by_indexlength:
                samplesheet_name_bulk = (
                    flowcell_id
                    + "_samplesheet_"
                    + str(index_length_sample_list["index_length"][0])
                    + "_"
                    + str(index_length_sample_list["index_length"][1])
                )

                merge_sample_index_info = {}
                for sample in index_length_sample_list["samples"]:
                    if sample in categorised_sample_dict["other_samples"]:
                        merge_sample_index_info[sample] = categorised_sample_dict["other_samples"][sample]

                # split samples into multiple entries based on lane values
                split_samples_dict = {}
                for sample, details in merge_sample_index_info.items():
                    lanes = details["Lane"]  # Get the list of lanes
                    for lane in lanes:
                        # Create a new key for each unique (sample, lane) combination
                        unique_key = f"{sample}_Lane_{lane}"
                        # Copy the sample details and replace the Lane value with the current lane
                        split_samples_dict[unique_key] = {**details, "Lane": lane}

                # Obtain the cycle length
                cycle_length = extract_cycle_fromxml(runinfo_path)
                for sample in split_samples_dict.items():
                    index_string = sample[1]["index"]
                    index2_string = sample[1].get("index2", None)
                # Check if Index length and Cycle length match
                if not (index_length_sample_list["index_length"][0] == cycle_length[1] and index_length_sample_list["index_length"][1] == 0) or (
                    index_length_sample_list["index_length"][0] == cycle_length[1] and index_length_sample_list["index_length"][1] == cycle_length[1]
                ):
                    if index2_string:
                        override_string = generate_overridecycle_string(
                            index_string, int(cycle_length[1]), int(cycle_length[0]), index2_string, int(cycle_length[2]), int(cycle_length[3])
                        )
                    else:
                        override_string = generate_overridecycle_string(index_string, int(cycle_length[1]), int(cycle_length[0]))
                    bcl_settings_dict["OverrideCycles"] = override_string

                # Generate samplesheet with the updated settings
                samplesheet_path = os.path.join(output_path, samplesheet_name_bulk + ".csv")
                generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, split_samples_dict, samplesheet_path)

    # # Generate samplesheet with the updated settings
    # samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
    # generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, filtered_samples, samplesheet_path)
