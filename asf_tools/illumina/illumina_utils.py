# i'll write the functionality function then split it into a class with subfunctions

# i need to parse through runinfo and save this info in a dict
# dict would eventually be saved as a file or info added to a database

import re
from datetime import datetime

import xmltodict


class IlluminaUtils:

    def runinfo_xml_to_dict(self, runinfo_file) -> dict:
        """
        Converts an XML RunInfo file into a Python dictionary.

        This method reads the contents of a RunInfo XML file, parses it using the
        `xmltodict` library, and returns the parsed data as a dictionary.

        Args:
            runinfo_file (str): The file path to the RunInfo XML file.

        Returns:
            dict: A dictionary representation of the XML file content.
        """
        with open(runinfo_file, "r", encoding="utf-8") as runinfo_file:
            runinfo_file_content = runinfo_file.read()

        full_runinfo_dict = xmltodict.parse(runinfo_file_content)
        return full_runinfo_dict

    def find_key_recursively(self, d: dict, target_key: str) -> list:
        """
        Recursively searches for a target key in a nested dictionary.

        Args:
        d (dict): The dictionary to search through.
        target_key (str): The key to find.

        Returns:
        list: A list of values associated with the target key.
        """
        results = []

        # If the dictionary has the target key at the top level, add the value to results
        if target_key in d:
            results.append(d[target_key])

        # Otherwise, continue searching recursively in nested dictionaries or lists
        for key, value in d.items():
            if isinstance(value, dict):
                results.extend(self.find_key_recursively(value, target_key))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        results.extend(self.find_key_recursively(item, target_key))

        return results

    def extract_matching_item_from_xmldict(self, item_list: list, item_name: str):
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
            ValueError: If the item is not found in the list.
        """
        item_results = self.find_key_recursively(item_list, item_name)
        item = item_results[0] if item_results else None

        if item is None:
            raise ValueError(f"No {item_name} found in the XML structure.")

        return item

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
        """

        # Extract info from the dictionary as required
        run_id = self.extract_matching_item_from_xmldict(runinfo_dict, "@Id")
        instrument = self.extract_matching_item_from_xmldict(runinfo_dict, "Instrument")

        machine_mapping = {"^M": "MiSeq", "^K": "HiSeq 4000", "^D": "HiSeq 2500", "^N": "NextSeq", "^A": "NovaSeq", "^LH": "NovaSeqX"}
        for pattern, machine_name in machine_mapping.items():
            if re.match(pattern, instrument):
                machine = machine_name
            else:
                raise ValueError("Machine type not recognised")

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        runinfo_dict = {"current_date": current_datetime, "run_id": run_id, "instrument": instrument, "machine": machine}
        # print(runinfo_dict)
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
        run_id = self.extract_matching_item_from_xmldict(runinfo_dict, "@Id")
        reads_fullinfo = self.extract_matching_item_from_xmldict(runinfo_dict, "Reads")

        # Extract single or paired end info for each read
        end_type_count = 0
        read_data = []

        for read in reads_fullinfo["Read"]:
            number = read["@Number"]
            num_cycles = read["@NumCycles"]
            is_indexed_read = read["@IsIndexedRead"]

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
        print(readinfo_dict)

        return readinfo_dict

    def merge_runinfo_dict_fromfile(self, runinfo_file) -> dict:
        original_dict = self.runinfo_xml_to_dict(runinfo_file)
        filtered_dict = self.filter_runinfo(original_dict)
        reads_dict = self.filter_readinfo(original_dict)

        merged_dict = filtered_dict
        # for key, value in reads_dict.items():
        #     for sub_key, sub_value in value.items():
        #         if key in merged_dict:
        #             merged_dict[key][sub_key] = sub_value
        # print(merged_dict)

        return merged_dict

# my $insert = {'SampleSheet_Trigger' => 'N', 'SampleSheet_TimeStamp' => $sst, 'SampleSheet' => $ss, 'End_Type' => $end_type}
