import os
import re
from datetime import datetime
from xml.parsers.expat import ExpatError

import xmltodict


class IlluminaUtils:
    """Class for extracting read run information from the RunInfo.xml file"""

    def runinfo_xml_to_dict(self, runinfo_file) -> dict:
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

    def find_key_recursively(self, dic: dict, target_key: str) -> list:
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
                results.extend(self.find_key_recursively(value, target_key))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        results.extend(self.find_key_recursively(item, target_key))

        return results

    def extract_matching_item_from_dict(self, item_dict: dict, item_name: str):
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
        item_results = self.find_key_recursively(item_dict, item_name)
        item = item_results[0] if item_results else None

        if item is None:
            raise TypeError(f"{item_name} not found in the XML structure.")

        return item

    def extract_illumina_runid_fromxml(self, runinfo_file) -> str:
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
        runinfo_dict = self.runinfo_xml_to_dict(runinfo_file)
        container_name = self.extract_matching_item_from_dict(runinfo_dict, "Flowcell")

        return container_name

    def extract_illumina_runid_frompath(self, path: str, file_name: str) -> str:
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
                runid = self.extract_illumina_runid_fromxml(xml_file)
                return runid

    def filter_runinfo(self, runinfo_dict: dict) -> dict:
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
        run_id = self.extract_matching_item_from_dict(runinfo_dict, "@Id")
        instrument = self.extract_matching_item_from_dict(runinfo_dict, "Instrument")

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

        runinfo_dict = {"current_date": current_datetime, "run_id": run_id, "instrument": instrument, "machine": machine}
        return runinfo_dict

    def filter_readinfo(self, runinfo_dict: dict) -> dict:
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
        run_id = self.extract_matching_item_from_dict(runinfo_dict, "@Id")
        reads_fullinfo = self.extract_matching_item_from_dict(runinfo_dict, "Reads")

        # Extract single or paired end info for each read
        end_type_count = 0
        read_data = []

        for read in reads_fullinfo["Read"]:
            number = self.extract_matching_item_from_dict(read, "@Number")
            num_cycles = self.extract_matching_item_from_dict(read, "@NumCycles")
            is_indexed_read = self.extract_matching_item_from_dict(read, "@IsIndexedRead")

            if is_indexed_read == "N":
                read_data.append({"read": f"Read {number}", "num_cycles": f"{num_cycles} Seq"})
                end_type_count += 1
            elif is_indexed_read == "Y":
                read_data.append({"read": f"Read {number}", "num_cycles": f"{num_cycles} Seq"})

        end_type = "SR"
        if end_type_count > 1:
            end_type = "PE"

        # Collect the extracted info in a single dictionary
        readinfo_dict = {}
        readinfo_dict["run_id"] = run_id
        readinfo_dict["end_type"] = end_type
        readinfo_dict["reads"] = read_data

        return readinfo_dict

    def merge_dicts(self, dict1, dict2, key):
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

    def merge_runinfo_dict_fromfile(self, runinfo_file) -> dict:
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
        original_dict = self.runinfo_xml_to_dict(runinfo_file)
        filtered_dict = self.filter_runinfo(original_dict)
        reads_dict = self.filter_readinfo(original_dict)

        # Merge the dictionaries
        merged_result = self.merge_dicts(filtered_dict, reads_dict, "run_id")

        return merged_result
