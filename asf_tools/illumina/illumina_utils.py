import csv
import logging
import os
import re
from datetime import datetime
from enum import Enum
from xml.parsers.expat import ExpatError

import xmltodict


log = logging.getLogger(__name__)
logging.basicConfig(
    filename="logfile.log",  # Name of the log file (stored locally)
    filemode="w",  # "w" to overwrite each time, use "a" to append
    level=logging.DEBUG,  # Log INFO and above (INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",
)


class IndexMode(Enum):
    SINGLE_INDEX = "single_index"
    DUAL_INDEX = "dual_index"


def runinfo_xml_to_dict(runinfo_file) -> dict:
    """
    Converts an XML RunInfo file into a Python dictionary.

    This method reads the contents of a RunInfo XML file, parses it using the
    `xmltodict` library, and returns the parsed data as a dictionary.

    Args:
        runinfo_file (str): The file path to the RunInfo XML file.

    Returns:
        dict: A dictionary representation of the XML file content.

    Raises:
        FileNotFoundError: If the file does not exist or cannot be opened.
        IOError: For other file-related errors.
        ExpatError: If the XML is not formatted correctly.
    """
    if not os.path.isfile(runinfo_file):
        raise FileNotFoundError(f"{runinfo_file} does not exist or is not a file.")

    # Convert xml file into a dict or raise an error to warn that the file is not xml formatted
    with open(runinfo_file, "r", encoding="utf-8") as runinfo_file:
        runinfo_file_content = runinfo_file.read()

        try:
            full_runinfo_dict = xmltodict.parse(runinfo_file_content)
            return full_runinfo_dict
        except ExpatError as exc:
            # Return error if xml is not formatted according to the xml schema
            raise ExpatError(f"{runinfo_file_content} content is compromised or not xml format") from exc


def find_key_recursively(dic: dict, target_key: str) -> list:
    """
    Recursively searches for a target key in a nested dictionary.

    Args:
        d (dict): The dictionary to search through.
        target_key (str): The key to find.

    Returns:
        list: A list of values associated with the target key.

    Raises:
        ValueError: If the provided argument is not a dictionary or if `target_key` is not a non-empty string.
    """
    if not isinstance(dic, dict):
        raise ValueError("The provided argument is not a dictionary.")
    if not isinstance(target_key, str) or target_key == "":
        raise ValueError("target_key must be a non-empty string.")

    results = []

    # If the dictionary has the target key at the top level, add the value to results
    if target_key in dic:
        results.append(dic[target_key])

    # Otherwise, continue searching recursively in nested dictionaries or lists
    for key, value in dic.items():  # pylint: disable=unused-variable
        if isinstance(value, dict):
            results.extend(find_key_recursively(value, target_key))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    results.extend(find_key_recursively(item, target_key))

    return results


def extract_matching_item_from_dict(item_dict: dict, item_name: str):
    """
    Extracts the first occurrence of a specified item from a list.

    This method searches for the first occurrence of a given item within a list
    by recursively searching the list structure. If the item is found, it returns
    the first instance. If the item is not found, it raises a `ValueError`.

    Args:
        item_list (list): The list to search within.
        item_name (str): The name of the item to search for.

    Returns:
        str: The first occurrence of the specified item in the list.

    Raises:
        TypeError: If the item is not found in the list.
    """
    item_results = find_key_recursively(item_dict, item_name)
    item = item_results[0] if item_results else None

    if item is None:
        raise TypeError(f"{item_name} not found in the XML structure.")

    return item


def extract_illumina_runid_fromxml(runinfo_file) -> str:
    """
    Extract the Illumina Run ID (Flowcell ID) from an XML RunInfo file.

    This method converts the given XML RunInfo file into a dictionary, then extracts the
    Flowcell ID (run ID) by locating the matching item within the dictionary.

    Args:
        runinfo_file (str): The path to the XML RunInfo file from which to extract the Run ID.

    Returns:
        str: The extracted Flowcell ID (Run ID) from the XML file.

    Raises:
        ValueError: If the runinfo_file is invalid or does not contain a Flowcell ID.
        TypeError: If the item is not found in the list.
    """
    runinfo_dict = runinfo_xml_to_dict(runinfo_file)
    container_name = extract_matching_item_from_dict(runinfo_dict, "Flowcell")

    return container_name


def extract_illumina_runid_frompath(path: str, file_name: str) -> str:
    """
    Extract the Illumina Run ID (Flowcell ID) by searching for a specific XML file in a directory path.

    This method traverses the directory structure starting from the given `path`, searching for a file
    with the specified `file_name`. Once found, it extracts the Illumina Run ID (Flowcell ID) by parsing
    the XML file.

    Args:
        path (str): The root directory to begin the search for the XML file.
        file_name (str): The name of the XML file to look for in the directory structure.

    Returns:
        str: The extracted Flowcell ID (Run ID) from the found XML file.

    Raises:
        FileNotFoundError: If the specified file is not found within the given path.
        ValueError: If the runinfo_file is invalid or does not contain a Flowcell ID.
        TypeError: If the item is not found in the list.
    """
    for dirpath, dirnames, filenames in os.walk(path):  # pylint: disable=unused-variable
        if file_name in filenames:
            xml_file = os.path.join(dirpath, file_name)
            runid = extract_illumina_runid_fromxml(xml_file)
            return runid


def extract_cycle_fromxml(runinfo_file) -> str:
    """
    Extract the Illumina Cycle length (NumCycles) from an XML RunInfo file.

    This method converts the given XML RunInfo file into a dictionary, then extracts the
    NumCycles by locating the matching item within the dictionary.

    Args:
        runinfo_file (str): The path to the XML RunInfo file from which to extract the Run ID.

    Returns:
        str: The extracted NumCycles from the XML file.

    Raises:
        ValueError: If the runinfo_file is invalid or does not contain a NumCycles value.
        TypeError: If the item is not found in the list.
    """
    runinfo_dict = runinfo_xml_to_dict(runinfo_file)
    container_name = find_key_recursively(runinfo_dict, "@NumCycles")

    return container_name


def extract_cycle_frompath(path: str, file_name: str) -> str:
    """
    Extract the NumCycles value by searching for a specific XML file in a directory path.

    This method traverses the directory structure starting from the given `path`, searching for a file
    with the specified `file_name`. Once found, it extracts the NumCycles value by parsing
    the XML file.

    Args:
        path (str): The root directory to begin the search for the XML file.
        file_name (str): The name of the XML file to look for in the directory structure.

    Returns:
        str: The extracted NumCycles from the found XML file.

    Raises:
        FileNotFoundError: If the specified file is not found within the given path.
        ValueError: If the runinfo_file is invalid or does not contain a Flowcell ID.
        TypeError: If the item is not found in the list.
    """
    for dirpath, dirnames, filenames in os.walk(path):  # pylint: disable=unused-variable
        if file_name in filenames:
            xml_file = os.path.join(dirpath, file_name)
            runid = extract_cycle_fromxml(xml_file)
            return runid


def filter_runinfo(runinfo_dict: dict) -> dict:
    """
    Filters and restructures information from a RunInfo dictionary.

    This method extracts specific information from the provided RunInfo dictionary,
    such as the run ID and instrument name. It then maps the instrument to its
    corresponding machine type using predefined patterns. If the instrument does not match any of the patterns, a `ValueError` is raised. The resulting dictionary
    includes the current date and time, the run ID, the instrument name, and the
    machine type.

    Args:
        runinfo_dict (dict): The dictionary containing the RunInfo data.

    Returns:
        dict: A dictionary containing filtered and structured RunInfo data,
            including the current date, run ID, instrument, and machine type.

    Raises:
        ValueError: If the instrument does not match any of the predefined patterns in `machine_mapping`.
    """

    # Extract info from the dictionary as required
    run_id = extract_matching_item_from_dict(runinfo_dict, "@Id")
    instrument = extract_matching_item_from_dict(runinfo_dict, "Instrument")
    lane = extract_matching_item_from_dict(runinfo_dict, "@LaneCount")

    # Determine the machine type used based on the initial letters of the string value in instrumet
    machine_mapping = {"^M": "MiSeq", "^K": "HiSeq 4000", "^D": "HiSeq 2500", "^N": "NextSeq", "^A": "NovaSeq", "^LH": "NovaSeqX"}
    machine = None
    for pattern, machine_name in machine_mapping.items():
        if re.match(pattern, instrument):
            machine = machine_name
            break
    # If there are no matches, it could be a new machine or incorrect information
    if machine is None:
        raise ValueError("Machine type not recognised")

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    runinfo_dict = {"current_date": current_datetime, "run_id": run_id, "instrument": instrument, "machine": machine, "lane": lane}
    return runinfo_dict


def filter_readinfo(runinfo_dict: dict) -> dict:
    """
    Filters and structures read information from a RunInfo dictionary.

    This method extracts details about sequencing reads from the provided RunInfo
    dictionary, including the run ID and information about each read (e.g., number
    of cycles, whether it is indexed). It determines if the sequencing run is
    single-end (SR) or paired-end (PE) based on the number of non-indexed reads.

    Args:
        runinfo_dict (dict): The dictionary containing the RunInfo data.

    Returns:
        dict: A dictionary containing the run ID, the sequencing end type (SR or PE),
            and a list of dictionaries with read-specific information such as the
            number of cycles for each read.
    """
    run_id = extract_matching_item_from_dict(runinfo_dict, "@Id")
    reads_fullinfo = extract_matching_item_from_dict(runinfo_dict, "Reads")

    # Extract single or paired end info for each read
    end_type_count = 0
    read_data = []

    for read in reads_fullinfo["Read"]:
        number = extract_matching_item_from_dict(read, "@Number")
        num_cycles = extract_matching_item_from_dict(read, "@NumCycles")
        is_indexed_read = extract_matching_item_from_dict(read, "@IsIndexedRead")

        if is_indexed_read == "N":
            read_data.append({"read": f"Read {number}", "num_cycles": f"{num_cycles}"})
            end_type_count += 1
        elif is_indexed_read == "Y":
            read_data.append({"read": f"Index {number}", "num_cycles": f"{num_cycles}"})

    end_type = "SR"
    if end_type_count > 1:
        end_type = "PE"

    # Collect the extracted info in a single dictionary
    readinfo_dict = {}
    readinfo_dict["run_id"] = run_id
    readinfo_dict["end_type"] = end_type
    readinfo_dict["reads"] = read_data

    return readinfo_dict


def merge_dicts(dict1, dict2, key):
    """
    Merges two dictionaries based on a common key.

    This method merges two dictionaries, keeping all information from both
    dictionaries. If a key exists in both dictionaries, the value from `dict1` is retained.

    Args:
        dict1 (dict): The first dictionary to merge.
        dict2 (dict): The second dictionary to merge.
        key (str): The key that both dictionaries share, used to merge them.

    Returns:
        dict: A new dictionary that contains all keys and values from both
            input dictionaries. If a key exists in both dictionaries, the value
            from `dict1` is retained.
    """
    # Initialize an empty dictionary to store the merged result
    merged_dict = {}

    # Combine the dictionaries
    all_keys = set(list(dict1.keys()) + list(dict2.keys()))

    for k in all_keys:
        if k == key:
            merged_dict[k] = dict1[k] if k in dict1 else dict2[k]
        else:
            merged_dict.update(dict1 if k in dict1 else {})
            merged_dict.update(dict2 if k in dict2 else {})

    return merged_dict


def merge_runinfo_dict_fromfile(runinfo_file) -> dict:
    """
    Merges RunInfo data from an XML file into a single dictionary.

    This method processes a RunInfo XML file by converting it into a dictionary,
    filtering the data, and extracting read information. It then merges the filtered
    RunInfo data with the extracted read information into a single dictionary based on
    a common key.

    Args:
        runinfo_file (str): The file path to the RunInfo XML file.

    Returns:
        dict: A dictionary containing merged RunInfo and read information,
            including details like run ID, instrument, machine type, and read data.

    Raises:
        FileNotFoundError: If the provided XML file does not exist or cannot be opened.
        KeyError: If required keys are missing in the XML structure or in the merge operation.
    """
    original_dict = runinfo_xml_to_dict(runinfo_file)
    filtered_dict = filter_runinfo(original_dict)
    reads_dict = filter_readinfo(original_dict)

    # Merge the dictionaries
    merged_result = merge_dicts(filtered_dict, reads_dict, "run_id")

    return merged_result


def reformat_barcode(samplesheet_dict: dict) -> dict:
    """
    Extracts and formats barcode sequences from a sample dictionary.

    This function takes a dictionary of samples, where each sample has associated details including a
    "barcode" field. It validates the input as a dictionary, then processes each sample's barcode by
    extracting the sequence within parentheses. If a hyphen ("-") is present in the barcode sequence, it
    splits the sequence into two parts and stores each part in a separate field.

    Args:
        samplesheet_dict (dict): A dictionary containing sample data, where each sample entry may include
            a "barcode" field.

    Returns:
        dict: A dictionary where each key is a sample identifier, and the value is a dictionary containing:
            - "index" (str): The extracted barcode sequence or the first part of the sequence if a hyphen is present.
            - "index2" (str, optional): The second part of the barcode sequence if a hyphen is present.

        None: If any sample entry is missing the "barcode" key, returns None.

    Raises:
        TypeError: If the input `samplesheet_dict` is not a dictionary.

    Example:
        Input:
            {
                "Sample1": {"barcode": "BC01 (AAGAAAGTTGTCGGTGTCTTTGTG)"},
                "Sample2": {"barcode": "BC02 (GTTCTT-CTGTGGGGAATACGAGT)"},
                "Sample3": {"barcode": "GTTCTT-CTGTGGGGAATA"},
            }

        Output:
            {
                "Sample1": {"index": "AAGAAAGTTGTCGGTGTCTTTGTG"},
                "Sample2": {"index": "GTTCTT", "index2": "CTGTGGGGAATACGAGT"},
                "Sample3": {"index": "GTTCTT-CTGTGGGGAATA"},
            }
    """
    # Check that input_string is a string
    if not isinstance(samplesheet_dict, dict):
        raise TypeError("The input value must be a dictionary.")

    # Initialize an empty dictionary to store the samples and their reformatted barcodes
    sample_index_dict = {}

    for sample, details in samplesheet_dict.items():
        # Skip samples without no information
        if details is None:
            continue

        if "barcode" in details:
            barcode_info = details["barcode"]
            barcode_sequence = ""

            # Extract the barcode sequence within parentheses, if present
            if "(" in barcode_info and ")" in barcode_info:
                barcode_sequence = barcode_info.split("(")[1].split(")")[0]
            else:
                barcode_sequence = barcode_info

            if "-" in barcode_sequence:
                # Split the barcode sequence by hyphens
                indices = barcode_sequence.split("-")

                # Generate a dictionary of indices dynamically (index, index2, ...)
                index_dict = {"index": indices[0]}
                index_dict.update({f"index{i + 2}": idx for i, idx in enumerate(indices[1:])})
                sample_index_dict[sample] = index_dict
            else:
                # If no hyphen, keep as a single index
                sample_index_dict[sample] = {"index": barcode_sequence}
        else:
            # Skip samples without barcode information
            continue

    return sample_index_dict


def atac_reformat_barcode(samplesheet_dict: dict) -> dict:
    """
    Extracts and formats barcode sequences from a sample dictionary.

    This function takes a dictionary of samples, where each sample has associated details,
    including a "barcode" field. It validates the input as a dictionary, then processes
    each sample's barcode by extracting the sequence within parentheses. If the barcode
    sequence contains hyphens ("-"), it splits the sequence into a list of substrings.

    Args:
        samplesheet_dict (dict): A dictionary containing sample data, where each sample entry
            may include a "barcode" field.

    Returns:
        dict: A dictionary where each key is a sample identifier, and the value is a dictionary containing:
            - "index" (list): A list of substrings created by splitting the extracted barcode sequence at hyphens.

        None: If any sample entry is missing the "barcode" key, returns None.

    Raises:
        TypeError: If the input `samplesheet_dict` is not a dictionary.

    Example:
        Input:
            {
                "Sample1": {"barcode": "BC01 (ATAACCTA-CGGTGAGC-GATCTTAT-TCCGAGCG)"},
                "Sample2": {"barcode": "BC02 (AAGAAAGTTGTCGGTGTCTTTGTG)"}
            }

        Output:
            {
                "Sample1": {"index": ["ATAACCTA", "CGGTGAGC", "GATCTTAT", "TCCGAGCG"]},
                "Sample2": {"index": ["AAGAAAGTTGTCGGTGTCTTTGTG"]}
            }
    """
    # Validate input type
    if not isinstance(samplesheet_dict, dict):
        raise TypeError("The input value must be a dictionary.")

    # Initialize an empty dictionary to store reformatted barcodes
    sample_index_dict = {}

    for sample, details in samplesheet_dict.items():
        if "barcode" in details:
            barcode_info = details["barcode"]

            # Extract the barcode sequence within parentheses, if present
            if "(" in barcode_info and ")" in barcode_info:
                barcode_sequence = barcode_info.split("(")[1].split(")")[0]
            else:
                barcode_sequence = barcode_info

            # Split the barcode sequence by hyphen into a list
            indices = barcode_sequence.split("-")

            # Store the list of substrings under the "index" key
            sample_index_dict[sample] = {"index": indices}
        else:
            # Skip samples without barcode information
            continue

    return sample_index_dict


def group_samples_by_index_length(sample_index_dict: dict) -> list:
    """
    Splits samples from a dictionary into groups based on the length of 'index' and 'index2'.

    This function takes a dictionary where each key is a sample ID and each value is another
    dictionary containing 'index' and optionally 'index2'. It determines the length of each
    'index' and 'index2' (if present), and groups the samples based on these lengths.

    Args:
        data (dict): Dictionary where keys are sample IDs and values are dictionaries
                    containing 'index' and optionally 'index2' keys.

    Returns:
        list of dict: A list of dictionaries, each containing:
                    - 'index_length': tuple representing (index_length, index2_length),
                    - 'samples': list of sample IDs with that index length combination.

    Raises:
        KeyError: If 'index' is missing from any sample's data.
    """
    # Check that input_string is a string
    if not isinstance(sample_index_dict, dict):
        raise TypeError("The input value must be a dictionary.")

    # Initialize a an empty dictionary to store samples by (index_length, index2_length) group
    result_dict = {}
    result = []

    for sample_id, indices in sample_index_dict.items():
        # Ensure 'index' value is present
        if "index" not in indices:
            # log.warning(f"Index value for '{sample_id}' not found.")
            pass
        else:
            # Calculate the length of 'index' and 'index2' (default to 0 if 'index2' is missing)
            index_length = len(indices["index"])
            index2_length = len(indices.get("index2", ""))

            # Create a tuple representing the (index_length, index2_length)
            length_tuple = (index_length, index2_length)

            # Add the sample ID to the appropriate group in the result dictionary
            if length_tuple not in result_dict:
                result_dict[length_tuple] = []
            result_dict[length_tuple].append(sample_id)

    # Convert the result_dict to the required list of dictionaries format
    result = [{"index_length": length_tuple, "samples": sample_ids} for length_tuple, sample_ids in result_dict.items()]

    return result


def group_samples_by_dictkey(samples_dict: dict, group_key: str) -> dict:
    """
    Groups sample identifiers by a specified key in the sample data.

    This function takes a dictionary of samples and organizes sample identifiers
    based on the values of a specified key in each sample's data. Each key value
    becomes a group in the resulting dictionary, where the group key maps to a list
    of sample identifiers that share that value.

    Args:
        samples_dict (dict): A dictionary of samples, where each key is a sample identifier
            and each value is a dictionary containing sample data.
        group_key (str): The key within each sample's data used to group the sample identifiers.

    Returns:
        dict: A dictionary with unique values of `group_key` as keys and lists of sample identifiers
            as values, representing groups of samples. Returns `None` if `group_key` is missing
            in any sample data or if any group key is not found in `grouped_samples`.

    Raises:
        ValueError: If `samples_dict` is not a dictionary.
    """
    if not isinstance(samples_dict, dict):
        raise ValueError("The provided argument is not a dictionary.")

    grouped_samples = {}

    for sample_id, sample_data in samples_dict.items():
        # Check that key is within the sample's dict
        if group_key not in sample_data:
            pass
        else:
            # Use the specified key for grouping
            key_value = sample_data[group_key]

            if key_value not in grouped_samples:
                grouped_samples[key_value] = []

            # Save sample IDs in a list
            grouped_samples[key_value].append(sample_id)

    return grouped_samples


def split_by_project_type(samples_all_info: dict, project_types_dict: dict) -> dict:
    """
    Dynamically categorizes samples based on project type and data analysis type.

    Args:
        samples_all_info (dict): Dictionary containing metadata for all samples.
        project_types_dict (dict): Dictionary mapping category names to lists of valid values.

    Returns:
        dict: A dictionary containing categorized samples for each project type.
    """
    # Check inputs are dictionaries
    if not isinstance(samples_all_info, dict):
        raise ValueError(f"{samples_all_info} is not a dictionary.")

    if not isinstance(project_types_dict, dict):
        raise ValueError(f"{project_types_dict} is not a dictionary.")

    # Filter sample_all_info to include only the lane, sample_id and indexing information in the correct format

    ## convert barcode value from "BC (ATGC)" to "ATGC". Return original barcode string if the barcode isn't in the "BC (ATGC)" format
    sample_and_index_dict = reformat_barcode(samples_all_info)

    ## filter dict to only keep sample_id, lane and index information
    simplified_samples_dict = {}
    for sample, metadata in samples_all_info.items():
        if not isinstance(metadata, dict):
            log.warning(f"Sample '{sample}' has invalid metadata format. Skipping.")
            continue

        simplified_samples_dict[sample] = {
            "Lane": metadata.get("lanes", []),  # Default to empty list if missing
            "Sample_ID": sample,
            **sample_and_index_dict.get(sample, {}),
        }

    ## expand the simplified dict so each entry only has 1 lane value
    expanded_simplified_samples_dict = {}
    for sample, details in simplified_samples_dict.items():
        lanes = details["Lane"]  # Get the list of lanes
        for lane in lanes:
            # create a new key for each unique (sample, lane) combination
            unique_key = f"{sample}_lane_{lane}"
            # copy the sample details and replace the Lane value with the current lane
            expanded_simplified_samples_dict[unique_key] = {**details, "Lane": lane}

    # Initialize result dictionary dynamically with empty dictionaries for each category
    categorised_samples = {category.lower(): {} for category in project_types_dict}

    # Categorize samples based on project type or data analysis type
    for sample, info in expanded_simplified_samples_dict.items():
        sample_id = info["Sample_ID"]
        # Extract project type and data analysis type from the full sample info dictionary
        project_type = samples_all_info[sample_id].get("project_type")
        data_analysis_type = samples_all_info[sample_id].get("data_analysis_type")

        if project_type is None and data_analysis_type is None:
            log.warning(f"'{sample}' has None project_type and None data_analysis_type.")
            continue

        categorized = False  # Flag to track if the sample was categorized

        # Dynamically check and assign samples to the correct category
        for category, valid_types in project_types_dict.items():
            if valid_types is not None:
                if project_type in valid_types or data_analysis_type in valid_types:
                    categorised_samples[category.lower()][sample] = expanded_simplified_samples_dict[sample]
                    categorized = True
                    break  # Stop checking once categorized

        # Handle other/bulk samples separately
        if not categorized:
            if "other_samples" not in categorised_samples:
                categorised_samples["other_samples"] = {}
            categorised_samples["other_samples"][sample] = expanded_simplified_samples_dict[sample]

    # Add the all the filtered sample information to the general "all_samples" category
    categorised_samples["all_samples"] = expanded_simplified_samples_dict

    return categorised_samples


def calculate_overridecycle_values(index_str: str, runinfo_index_len: int, runinfo_read_len: int):
    """
    Calculates and validates override cycle values based on index length and read length.

    This method verifies the types and values of the input parameters, ensuring they meet expected
    conditions, and then calculates key values needed for sequencing override cycles. Specifically, it
    computes the length of the provided index string, the difference between the expected index length
    and the actual length, and returns these along with the read length.

    Args:
        index_str (str): The sequencing index string whose length is calculated.
        runinfo_index_len (int): The expected index length for the sequencing run.
        runinfo_read_len (int): The total read length specified in the sequencing run.

    Returns:
        tuple: A tuple containing:
            - str_length (int): The length of the `index_str`.
            - diff_value (int): The difference between `runinfo_index_len` and `str_length`.
            - runinfo_read_len (int): The provided read length for the sequencing run.

    Raises:
        TypeError: If `index_str` is not a string, or if `runinfo_index_len` and `runinfo_read_len`
            are not integers.
        ValueError: If `index_str` is empty or None, if `runinfo_index_len` or `runinfo_read_len`
            are negative, or if `diff_value` (i.e., `runinfo_index_len - len(index_str)`) is negative.
    """
    # Check that input_string is a string
    if not isinstance(index_str, str):
        raise TypeError(f"The index value ({index_str}) must be a string.")

    # Check that input_integer and y_value are integers
    if not isinstance(runinfo_index_len, int):
        raise TypeError(f"The runinfo index length ({runinfo_read_len}) must be an integer.")
    if not isinstance(runinfo_read_len, int):
        raise TypeError(f"The runinfo read length ({runinfo_read_len}) must be an integer.")

    if index_str == "" or index_str is None:
        raise TypeError("The index value cannot be empty or None.")

    # Check for a non-negative input_integer and y_value
    if runinfo_index_len < 0:
        raise TypeError(f"The {runinfo_index_len} input must be non-negative.")
    if runinfo_read_len < 0:
        raise TypeError(f"The {runinfo_read_len} value must be non-negative.")

    # Calculate the difference: input_integer - str_length
    str_length = len(index_str)
    diff_value = runinfo_index_len - str_length

    if diff_value < 0:
        raise ValueError(f"Expected index length {runinfo_index_len} should be longer than index length {str_length}.")

    return str_length, diff_value, runinfo_read_len


def generate_overridecycle_string(
    index_str: str,
    runinfo_index_len: int,
    runinfo_read_len: int,
    index2_str: str = None,
    runinfo_index2_len: int = None,
    runinfo_read2_len: int = None,
) -> str:
    """
    Constructs a formatted override cycle string based on specified index and read lengths.

    This method calculates override cycle values for sequencing by calling `calculate_overridecycle_values`
    for one or two sets of provided index strings and lengths, and formats them into a single sequencing
    override cycle string.

    Args:
        index_str (str): The primary sequencing index string to measure for length and compute a difference value.
        runinfo_index_len (int): Expected length for the primary index string.
        runinfo_read_len (int): The total read length for the primary index.
        index2_str (str, optional): A secondary sequencing index string. Default is None.
        runinfo_index2_len (int, optional): Expected length for the secondary index string. Default is None.
        runinfo_read2_len (int, optional): The total read length for the secondary index. Default is None.

    Returns:
        str: A formatted override cycle string for sequencing. If both sets of inputs are provided:
            "Y{runinfo_read_len};N{runinfo_index_len_diff}I{index_str_len};I{index_str2_len}N{runinfo_index2_len_diff};Y{runinfo_read2_len}".
            If only the first set is provided: "N{runinfo_index_len}Y{runinfo_read_len};I{index_str_len};N{runinfo_index_len}Y{runinfo_read_len}".

    Raises:
        ValueError: If only a partial set of secondary parameters is provided, or if the primary or secondary
            input lengths and read lengths are invalid, raising errors as managed by `calculate_overridecycle_values`.
    """
    # Compute values for the first set of inputs
    index_str_len, runinfo_index_len_diff, runinfo_read_len = calculate_overridecycle_values(index_str, runinfo_index_len, runinfo_read_len)
    overridecycle_string = ""

    # Check if a second set of parameters is provided
    if index2_str and runinfo_index2_len and runinfo_read2_len:
        # Compute values for the second set of inputs
        index_str2_len, runinfo_index2_len_diff, runinfo_read2_len = calculate_overridecycle_values(index2_str, runinfo_index2_len, runinfo_read2_len)

        # Construct the overridecycle_string dynamically, skipping components with a value of 0
        components = []

        if runinfo_read_len > 0:
            components.append(f"Y{runinfo_read_len}")
        if index_str_len > 0 or runinfo_index_len_diff > 0:
            first_index = f"I{index_str_len}" if index_str_len > 0 else ""
            first_index += f"N{runinfo_index_len_diff}" if runinfo_index_len_diff > 0 else ""
            components.append(first_index)

        # Construct the overridecycle_string dynamically, skipping components with a value of 0
        if index_str2_len > 0 or runinfo_index2_len_diff > 0:
            second_index = f"I{index_str2_len}" if index_str2_len > 0 else ""
            second_index += f"N{runinfo_index2_len_diff}" if runinfo_index2_len_diff > 0 else ""
            components.append(second_index)
        if runinfo_read2_len > 0:
            components.append(f"Y{runinfo_read2_len}")

        # Return the full output format with both sets
        # Join the components with semicolons
        overridecycle_string = ";".join(components)

    elif index2_str is None and runinfo_index2_len is None and runinfo_read2_len is None:
        # Return the simplified format if only one string is provided
        overridecycle_string = f"N{runinfo_index_len}Y{runinfo_read_len};I{index_str_len};N{runinfo_index_len}Y{runinfo_read_len}"

    return overridecycle_string


def index_distance(seq1, seq2):
    """
    Calculates the Hamming distance between two sequences.

    This method compares two input sequences, `seq1` and `seq2`, and returns the number of positions
    where the characters differ between the two sequences. It assumes that both sequences are of the same length.

    Args:
        seq1 (str): The first sequence to compare.
        seq2 (str): The second sequence to compare.

    Returns:
        int: The Hamming distance, representing the number of differing positions between the sequences.

    Raises:
        ValueError: If the input sequences `seq1` and `seq2` have different lengths.
    """
    return sum(c1 != c2 for c1, c2 in zip(seq1, seq2))


def minimum_index_distance(sequences: str):
    """
    Finds the minimum Hamming distance between any two sequences in a list.

    This method calculates the pairwise Hamming distances between all sequences in the provided list
    and returns the smallest of those distances. The function assumes the input is a list of equal-length strings.

    Args:
        sequences (list of str): A list of sequences to compare.

    Returns:
        int: The minimum Hamming distance between any two sequences in the list.

    Raises:
        ValueError: If the input `sequences` list is empty or contains sequences of differing lengths.
    """
    min_distance = float("inf")
    num_sequences = len(sequences)

    for i in range(num_sequences):
        for j in range(i + 1, num_sequences):
            distance = index_distance(sequences[i], sequences[j])
            min_distance = min(min_distance, distance)

    return min_distance


def dlp_barcode_data_to_dict(csv_file_path: str, selected_name: str) -> dict:
    """
    Parses a CSV file and groups rows by a specified column. Each unique value in that column
    is mapped to a dictionary containing:
    - A list of values for each other column in the row, unless there's only one value,
    in which case the value is added directly.
    - Modifies the Sample_ID by adding the selected name as a prefix and replacing it inside the dictionary.

    Args:
        csv_file_path (str): Path to the CSV file to be processed.
        selected_name (str): The name to be added as a prefix to Sample_ID.

    Returns:
        dict: A dictionary where keys are modified Sample_ID values (selected_name_Sample_ID),
            and values are dictionaries with the other columns as keys and their corresponding values.
            If a column has only one value for a key, that value will be stored directly instead of a list.
    """
    if not os.path.isfile(csv_file_path):
        raise FileNotFoundError(f"{csv_file_path} does not exist or is not a file.")

    result = {}

    with open(csv_file_path, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            # Modify the Sample_ID to include the selected_name prefix
            modified_sample_id = f"{selected_name}_{row['Sample_ID']}"

            # Add the modified Sample_ID to results
            result[modified_sample_id] = {}

            # Group the row data by the modified Sample_ID
            for column, value in row.items():
                if column != "Sample_ID":
                    result[modified_sample_id][column] = value

            # After collecting the data for a row, replace Sample_ID with modified_sample_id
            result[modified_sample_id]["Sample_ID"] = modified_sample_id

    return result


def generate_bclconfig(machine: str, flowcell: str, header_parameters=None, bclconvert_parameters=None):
    """
    Creates a BCL configuration file in JSON format with a Header and BCLConvert_Settings sections.

    This function generates a JSON configuration file with default Header and BCLConvert_Settings values. If
    optional parameters (`header_parameters` or `bclconvert_parameters`) contain any of the primary keys (`FileFormatVersion`,
    `InstrumentPlatform`, `RunName`, `SoftwareVersion`, or `FastqCompressionFormat`), those values will be used
    instead of the hardcoded defaults.

    Args:
        machine (str): The platform (machine) value, dynamically provided.
        flowcell (str): The run name (flowcell) value, dynamically provided.
        header_parameters (dict, optional): A dictionary of additional header settings to override or add to the 'Header' section.
        bclconvert_parameters (dict, optional): A dictionary of additional BCLConvert_Settings to override or add to the 'BCLConvert_Settings' section.

    Structure of the generated JSON:
        {
            "Header": {
                "FileFormatVersion": 2,
                "InstrumentPlatform": <machine>,
                "RunName": <flowcell>,
                ... (additional Header settings if provided)
            },
            "BCLConvert_Settings": {
                "SoftwareVersion": "4.2.7",
                "FastqCompressionFormat": "gzip",
                ... (additional BCLConvert_Settings if provided)
            }
        }

    Notes:
        - If `header_parameters` or `bclconvert_parameters` are provided, the function will merge those extra settings into the corresponding sections.
        - If a key already exists in the section, it will be overwritten by the provided value.
    """
    if not isinstance(machine, str):
        raise ValueError(f"{machine} must be a string.")
    if not isinstance(flowcell, str):
        raise ValueError(f"{flowcell} must be a string.")

    # Default values for core configuration keys
    header_defaults = {"FileFormatVersion": 2, "InstrumentPlatform": machine, "RunName": flowcell}

    bclconvert_defaults = {"SoftwareVersion": "4.2.7", "FastqCompressionFormat": "gzip"}

    # Initialize configuration data with defaults or provided values
    config_data = {
        "Header": {**header_defaults, **(header_parameters or {})},
        "BCLConvert_Settings": {**bclconvert_defaults, **(bclconvert_parameters or {})},
    }

    return config_data


def generate_bcl_samplesheet(
    header_dict: dict,
    reads_dict: dict,
    bcl_settings_dict: dict = None,
    bcl_data_dict: dict = None,
    output_file_path: str = "samplesheet.csv",
):
    """
    Generates a BCL sample sheet in CSV format, including sections for header, reads, BCLConvert settings, and BCLConvert data.

    Args:
        header_dict (dict): Dictionary containing the header information. Keys represent the field names, and values represent the field values.
        reads_dict (dict): Dictionary containing read information. Keys represent the read number or other identifiers, and values represent read lengths or other associated data.
        bcl_settings_dict (dict, optional): Dictionary for the BCLConvert settings section. Keys represent setting names, and values represent setting values. Defaults to None.
        bcl_data_dict (dict, optional): Dictionary containing the BCLConvert data for samples. Each value should be a dictionary representing a sample with keys as the field names (columns) and values as the data. Defaults to None.
        output_file_name (str, optional): Name of the output CSV file without extension. Defaults to "samplesheet".

    Returns:
        None: This function writes the output directly to a CSV file and does not return any value.

    Example:
        header_dict = {"FileFormatVersion": "2", "InvestigatorName": "John Doe"}
        reads_dict = {"Read1Cycles": "151", "Read2Cycles": "151"}
        bcl_settings_dict = {"BarcodeMismatchesIndex1": "1", "BarcodeMismatchesIndex2": "1"}
        bcl_data_dict = {
            "Sample1": {"Sample_ID": "Sample1", "Sample_Name": "Control", "Index": "AAGTCC"},
            "Sample2": {"Sample_ID": "Sample2", "Sample_Name": "Test", "Index": "CGTAAG"},
        }
        generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, bcl_data_dict, "output_samplesheet")
    """
    # Open the output file
    with open(output_file_path, "w", encoding="ASCII") as f:
        # Write the Header section
        if header_dict:
            f.write("[Header],,,\n")
            for key, value in header_dict.items():
                f.write(f"{key},{value},,\n")

        # Write the Reads section
        if reads_dict:
            f.write("\n[Reads],,,\n")
            for key, value in reads_dict.items():
                f.write(f"{key},{value},,\n")

        # Add the [BCLConvert_Settings] section at the bottom
        if bcl_settings_dict:
            f.write("\n[BCLConvert_Settings],,,\n")
            for key, value in bcl_settings_dict.items():
                f.write(f"{key},{value},,\n")

        # Add the [BCLConvert_Data] section after the settings at the bottom
        if bcl_data_dict:
            f.write("\n[BCLConvert_Data],,,\n")
            # Collect all unique column headers from samples_dict
            headers = set()
            for sample_info in bcl_data_dict.values():
                headers.update(sample_info.keys())

            # Write the column headers to the file
            headers = sorted(headers)
            f.write(",".join(headers) + "\n")

            # Write each sample's data
            for sample_id, sample_info in bcl_data_dict.items():  # pylint: disable=unused-variable
                f.write(",".join([str(sample_info.get(h, "")) for h in headers]) + "\n")


def count_samples_in_bcl_samplesheet(file_path: str, search_string: str) -> int:
    """
    Counts the number of non-empty lines from the first occurrence of a substring in a CSV file,
    excluding the matching line.

    This function scans each row of a CSV file to find the first occurrence of a
    specified substring. Once the substring is found, it counts the remaining non-empty
    lines from that point to the end of the file, excluding the matching row and any empty rows.

    Args:
        file_path (str): The file path to the CSV file.
        search_string (str): The substring to search for in the rows.

    Returns:
        int: The count of non-empty lines from the first match (excluding the match row)
            to the end of the file. Returns 0 if the file is empty or no match is found.

    Raises:
        FileNotFoundError: If the provided file does not exist or cannot be opened.
        ValueError: If the search_string is empty or is empty.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")

    if not isinstance(search_string, str):
        raise ValueError(f"{search_string} must be a string.")

    with open(file_path, "r", newline="", encoding="ASCII") as file:
        reader = csv.reader(file)
        # Convert all rows to a list to allow multiple passes over the data
        rows = list(reader)
        match_found = False
        lines_count = 0

        for row in rows:
            if match_found:
                # Count the row if it's non-empty
                if any(cell.strip() for cell in row):  # check if row is not empty
                    lines_count += 1
            elif any(search_string in cell for cell in row):
                # Mark that a match was found, but do not count this row
                match_found = True

        return lines_count if match_found else None
