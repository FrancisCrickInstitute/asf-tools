import json
import os

from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims
from asf_tools.illumina.illumina_utils import IlluminaUtils


################
# 1) split all samples based on len, eg :
# samples= []
# add sample1 to samples
# if len(sample2) ==len(sample1)  , then add to samples
# if len(sample2) != len(sample1) , then add to a different list
# if len(sample3) != to len(sample1) OR len(sample2) , then add to a different list
# etc until samples are finished


# 2) extract index info from the runinfo xml File
# 3) check if index info len is == len(sample)
# if NOT equal, then extract cycle info etc and run generate_overridecycle_string
# THEN add overridecycle_string to the dict with the bcl convert settings info


# 4) create the bcl dicts for the samplesheet

################

# # each dict within the split_samples_by_indexlength list has a collection of sample ids split according to both its index and index2 values

# # create subsetted dict with sample,index,index2 THEN
# # add step to check if index length==length in runinfo
# # if FALSE (ie. index different), run generate_overridecycle_string


# cycle_length = iu.extract_cycle_fromxml(runinfo_file)

# # All subsequent steps are run for each entry in split_samples_by_indexlength until a samplesheet has been created for all of them
# for entry in split_samples_by_indexlength:
#     filtered_samples = {}
#     if (index_length[0] == num_cycles and index_length[1] == 0) or (index_length[0] == num_cycles and index_length[1] == num_cycles):
#         for sample in entry["samples"]:
#             if sample in sample_and_index_dict:
#                     filtered_samples[sample] = sample_and_index_dict[sample]

# # eventually, collect all the dicts and run generate_bcl_samplesheet

# samplesheet_v1 = generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, bcl_data_dict, output_file_name: str = "samplesheet")
# if os.path.exist("samplesheet.csv"):

# # split_by_index_length = self.


# generate_overridecycle_string(reads_dict[read], reads_dict[num_cycles], reads_dict[num_cycles])


################################################################################################

# def generate_bcl_config():

################################################################################################


def generate_illumina_demux_samplesheets(runinfo_file, bcl_config_path=None):
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
    cl = ClarityHelperLims()

    # Obtain sample information and format it as required by `BCLConvert_Data`
    flowcell_id = iu.extract_illumina_runid_fromxml(runinfo_file)
    samples_all_info = cl.collect_samplesheet_info(flowcell_id)
    sample_and_index_dict = iu.reformat_barcode(samples_all_info) # Convert barcode value from "BC (ATGC)" to "ATGC"

    # If no BCL Config file is provided, generate a basic config file with relevant information
    if not bcl_config_path:
        xml_filtered = iu.filter_runinfo(runinfo_file)
        machine_type = xml_filtered["machine"]
        config_json = iu.generate_bclconfig(machine_type, flowcell_id)

        bcl_config_path_gen = "bcl_config" + "_" + flowcell_id + ".json"
        with open(bcl_config_path_gen, "w") as file:
            json.dump(config_json, bcl_config_path_gen, indent=4)

    # Extract info from the BCL Config file
    with open(bcl_config_path, "r") as file:
        config_json = json.load(file)

    header_dict = config_json["Header"]
    bcl_settings_dict = config_json["BCLConvert_Settings"]
    xml_content_dict = iu.runinfo_xml_to_dict(runinfo_file)
    reads_dict = iu.filter_readinfo(xml_content_dict)

    # Split samples by project type
    split_samples_by_projecttype = iu.group_samples_by_dictkey(samples_all_info, "project_type")

    # Subdivide samples into different workflows based on project type
    # Can be: DLP+, 10X ATAC, 10X, or Bulk/non-10X
    for project_type, samples in split_samples_by_projecttype.items():
        # Filter samples based on project type
        filtered_samples = {}
        for sample in samples:
            filtered_samples[sample] = sample_and_index_dict[sample]

        if "DLP" in project_type:
            # Workflow not determined yet
            pass
        elif "Single Cell" in project_type:
            # All samples are expected to be dual index and one index length
            samplesheet_name = flowcell_id + "_" + "samplesheet" + "_" + "singlecell" + "_"
            iu.generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, filtered_samples, samplesheet_name)
        else:
            # This should include Bulk data and all other project types

            # Group samples based on Index length
            split_samples_by_indexlength = iu.group_samples_by_index_length(sample_and_index_dict)

            # Extract the Cycle length
            cycle_length = iu.extract_cycle_fromxml(runinfo_file)

            for index_length_sample_list in split_samples_by_indexlength:
                # Create a dictionary with a subset of samples and their index values based on their index length
                filtered_samples = {}
                for sample in index_length_sample_list["samples"]:
                    filtered_samples[sample] = sample_and_index_dict[sample]

                # Check if Index length and Cycle length match
                if (index_length_sample_list["index_length"][0] == cycle_length[1] and index_length_sample_list["index_length"][1] == 0) or (
                    index_length_sample_list["index_length"][0] == cycle_length[1] and index_length_sample_list["index_length"][1] == cycle_length[1]
                ):
                    samplesheet_name = "samplesheet" + "_" + project_type + str(index_length_sample_list["index_length"][0]) + "_" + str(index_length_sample_list["index_length"][1])
                else:
                    # Generate the OverrideCycle string
                    # Extracting an index string values
                    index_string = next(iter(filtered_samples.values()))["index"]
                    first_sample = next(iter(filtered_samples.values()))
                    index2_string = first_sample.get("index2")
                    if index2_string:
                        override_string = iu.generate_overridecycle_string(
                            index_string, cycle_length[1], cycle_length[0], index2_string, cycle_length[2], cycle_length[3]
                        )
                    else:
                        override_string = iu.generate_overridecycle_string(index_string, cycle_length[1], cycle_length[0])
                    bcl_settings_dict["OverrideCycles"] = override_string

                # Generate samplesheet with the updated settings
                iu.generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, filtered_samples, samplesheet_name)


if __name__ == "__main__":
    generate_illumina_demux_samplesheets("./tests/data/illumina/RunInfo.xml")
