import json
import os
import warnings

from asf_tools.illumina.illumina_utils import IlluminaUtils


def generate_illumina_demux_samplesheets(cl, runinfo_file, output_path, bcl_config_path=None, dlp_sample_file=None):
    """
    The overall functionality is split into 2 sections: one is gathering and formatting sample information as required for further processing, while the second part is gathering BCL_convert specific information.

    The gathering and reformatting of the sample information allows the function to create different samplesheets for single/dual index samples, as well as help the user identify possibly problematic samples earlier.
    Meanwhile the second part of the code helps tailor setting values based on the sample type, eg. adding an `OverrideCycle` parameter when the index length does not match the Cycle length defined in the RuniInfo.xml file.

    The first part of this function is designed to take a RunInfo.xml file as an input and then perform these steps:
    1) extract RunID value (Flowcell ID) from the RunInfo.xml file.
    2) extract Cycle length value (NumCycles) from the RunInfo.xml file.
    3) use the RunID value to generate a dict of dicts (`samples_all_info`) with this information for each sample:
        sample_name (str): {
            "group": lab (str),
            "user": user_fullname (str),
            "project_id": project_id (str),
            "project_type": project_type (str or None),
            "reference_genome": reference_genome (str or None),
            "data_analysis_type": data_analysis_type (str or None),
            "barcode": reagent_barcode (str)
        },
    4) extract information from `samples_all_info` and format it as required by the `BCLConvert_Data` section of the final samplesheets, this includes:
        - filter `samples_all_info` to only keep the "sample_name" and "barcode" information
        - reformat "barcode" value and assign to "index" (also to "index2" where approriate)
        then save it in `sample_and_index_dict`
    5) evaluate Index length for each sample and group them based on the index length value. the groups and associated samples are saved in the `split_samples_by_indexlength` list
    6) create a subset of `sample_and_index_dict` for each group listed in `split_samples_by_indexlength`
    7) if the Cycle length does not match the Index length, calculate the new OverrideCycle value
    """
    # Initialise classes
    iu = IlluminaUtils()

    # Obtain sample information and format it as required by `BCLConvert_Data`
    flowcell_id = iu.extract_illumina_runid_fromxml(runinfo_file)
    samples_all_info = cl.collect_samplesheet_info(flowcell_id)
    sample_and_index_dict = iu.reformat_barcode(
        samples_all_info
    )  # Convert barcode value from "BC (ATGC)" to "ATGC". Return original barcode string if the barcode isn't in the "BC (ATGC)" format

    # If no BCL Config file is provided, generate a basic config file with relevant information
    if not bcl_config_path:
        xml_to_dict = iu.runinfo_xml_to_dict(runinfo_file)
        xml_filtered = iu.filter_runinfo(xml_to_dict)
        machine_type = xml_filtered["machine"]
        config_json = iu.generate_bclconfig(machine_type, flowcell_id)

        bcl_config_path = os.path.join(output_path, "bcl_config_" + flowcell_id + ".json")
        with open(bcl_config_path, "w") as file:
            json.dump(config_json, file, indent=4)

    # Extract info from the BCL Config file
    with open(bcl_config_path, "r") as file:
        config_json = json.load(file)

    header_dict = config_json["Header"]
    bcl_settings_dict = config_json["BCLConvert_Settings"]
    xml_content_dict = iu.runinfo_xml_to_dict(runinfo_file)

    # Obtain read specific information and format it as required by BCLconvert
    reads_dict = iu.filter_readinfo(xml_content_dict)
    reads_list = reads_dict["reads"]
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

    # Split samples by project type
    split_samples_by_projecttype = iu.group_samples_by_dictkey(samples_all_info, "project_type")

    # Subdivide samples into different workflows based on project type
    # Fist we categorise different values for "project_type"
    dlp_project_types = ["DLP"]
    single_cell_project_types = [
        "Single Cell",
        "10X",
        "10x Multiomics",
        "10x multiome",
        "10X-3prime",
        "10X-3prime-nuclei",
        "10X-Multiomics-GEX",
        "10X-FeatureBarcoding",
    ]
    atac_project_types = ["ATAC", "10X ATAC", "10X-ATAC", "10X Multiomics ATAC", "10X-Multiomics-ATAC"]

    # Then we assign each sample to the appropriate project group
    dlp_samples = {}
    single_cell_samples = {}
    atac_samples = {}
    other_samples = {}

    ## Identify the project type and add to the appropriate dictionary
    for project_type, samples in split_samples_by_projecttype.items():

        # Filter samples based on project type
        filtered_samples = {}
        for sample in samples:
            # Add 'Sample_ID' to the dictionary for each sample
            filtered_samples[sample] = {
                "Lane": samples_all_info[sample]["lanes"],
                "Sample_ID": sample,
                **(sample_and_index_dict.get(sample, {}) if sample_and_index_dict else {}),
            }
            data_analysis_type = samples_all_info[sample]["data_analysis_type"]

        # Ensure that project_type has a value other than None (ie. not associated with control samples or edge cases)
        if project_type is None:
            warnings.warn(f"'{samples}' have None project_type.", UserWarning)
            pass
        else:
            iu.populate_dict_with_sample_data(project_type, data_analysis_type, dlp_project_types, filtered_samples, dlp_samples)
            iu.populate_dict_with_sample_data(project_type, data_analysis_type, single_cell_project_types, filtered_samples, single_cell_samples)
            iu.populate_dict_with_sample_data(project_type, data_analysis_type, atac_project_types, filtered_samples, atac_samples)
        if not dlp_samples and not single_cell_samples and not atac_samples:
            other_samples.update(filtered_samples)

    # Set up variables required for the samplesheet generation
    samplesheet_name = "samplesheet"

    # Initiate processing only if samples are present for each workflow
    if dlp_samples:
        filtered_samples = {}
        for sample in dlp_samples:
            data_dict = iu.dlp_barcode_data_to_dict(dlp_sample_file, sample)
            filtered_samples.update(data_dict)
        samplesheet_name = f"{flowcell_id}_samplesheet_dlp"

        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
        iu.generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, dlp_samples, samplesheet_path)

    # This should include 10X/single cell data
    if single_cell_samples:
        # All samples are expected to be dual index and one index length
        samplesheet_name = f"{flowcell_id}_samplesheet_singlecell"

        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
        iu.generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, single_cell_samples, samplesheet_path)

    # This should include ATAC data
    if atac_samples:
        # All samples are expected to be single index and one index length
        samplesheet_name = f"{flowcell_id}_samplesheet_atac"

        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
        iu.generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, atac_samples, samplesheet_path)

    if other_samples:
        split_samples_by_indexlength = iu.group_samples_by_index_length(other_samples)
        for index_length_sample_list in split_samples_by_indexlength:
            samplesheet_name = (
                flowcell_id
                + "_samplesheet_"
                + str(index_length_sample_list["index_length"][0])
                + "_"
                + str(index_length_sample_list["index_length"][1])
            )

            # split samples into multiple entries based on lane values
            split_samples_dict = {}
            for sample, details in filtered_samples.items():
                lanes = details["Lane"]  # Get the list of lanes
                for lane in lanes:
                    # Create a new key for each unique (sample, lane) combination
                    unique_key = f"{sample}_Lane{lane}"
                    # Copy the sample details and replace the Lane value with the current lane
                    split_samples_dict[unique_key] = {**details, "Lane": lane}
            filtered_samples = split_samples_dict

            # Obtain the cycle length
            cycle_length = iu.extract_cycle_fromxml(runinfo_file)
            for sample in filtered_samples.items():
                index_string = sample[1]["index"]
                index2_string = sample[1].get("index2", None)
            # Check if Index length and Cycle length match
            if not (index_length_sample_list["index_length"][0] == cycle_length[1] and index_length_sample_list["index_length"][1] == 0) or (
                index_length_sample_list["index_length"][0] == cycle_length[1] and index_length_sample_list["index_length"][1] == cycle_length[1]
            ):
                if index2_string:
                    override_string = iu.generate_overridecycle_string(
                        index_string, int(cycle_length[1]), int(cycle_length[0]), index2_string, int(cycle_length[2]), int(cycle_length[3])
                    )
                else:
                    override_string = iu.generate_overridecycle_string(index_string, int(cycle_length[1]), int(cycle_length[0]))
                bcl_settings_dict["OverrideCycles"] = override_string

        # Generate samplesheet with the updated settings
        samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
        iu.generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, filtered_samples, samplesheet_path)

    # Calculate hamming distance for indexes

    # Generate samplesheet with the updated settings
    samplesheet_path = os.path.join(output_path, samplesheet_name + ".csv")
    iu.generate_bcl_samplesheet(header_dict, reformatted_reads_dict, bcl_settings_dict, filtered_samples, samplesheet_path)
