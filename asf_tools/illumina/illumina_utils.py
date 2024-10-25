import csv
import os
import re
from datetime import datetime
from enum import Enum
from xml.parsers.expat import ExpatError

import xmltodict
from bs4 import BeautifulSoup

from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims


class IndexMode(Enum):
    SINGLE_INDEX = "single_index"
    DUAL_INDEX = "dual_index"


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
        lane = self.extract_matching_item_from_dict(runinfo_dict, "@LaneCount")

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

    def generate_overridecycle_string(self, index_str: str, runinfo_index_len: int, runinfo_read_len: int) -> str:
        """
        Generates an override cycle string based on specified index and read lengths.

        This method constructs a formatted override cycle string for sequencing, using 
        provided lengths for the sequencing run's index and read. The output string 
        follows a set format that includes the read length, index string length, and 
        the difference between the specified index length and the actual length of the 
        provided index string.

        Args:
            index_str (str): The sequencing index string for which length will be calculated.
            runinfo_index_len (int): The expected index length for the sequencing run.
            runinfo_read_len (int): The total read length specified in the sequencing run.

        Returns:
            str: A formatted string representing sequencing cycles in the format 
                "Y{runinfo_read_len};I{index_length}N{n_value};I{index_length}N{n_value};Y{runinfo_read_len},"
                where `index_length` is the length of `index_str`, and `n_value` is the 
                difference between `runinfo_index_len` and `index_length`.

        Raises:
            TypeError: If `index_str` is not a string, `runinfo_index_len` or `runinfo_read_len` are 
                not integers, or if `index_str` is empty or None.
            ValueError: If `runinfo_index_len` or `runinfo_read_len` are negative, or if 
                the calculated difference (`n_value`) is negative.
        """
        # Check that input_string is a string
        if not isinstance(index_str, str):
            raise TypeError("The index value must be a string.")

        # Check that input_integer and y_value are integers
        if not isinstance(runinfo_index_len, int):
            raise TypeError("The runinfo index length must be an integer.")
        if not isinstance(runinfo_read_len, int):
            raise TypeError("The runinfo read length must be an integer.")

        if index_str == "" or index_str is None:
            raise TypeError("The index value cannot be empty or None.")

        # Check for a non-negative input_integer and y_value
        if runinfo_index_len < 0:
            raise TypeError(f"The {runinfo_index_len} input must be non-negative.")
        if runinfo_read_len < 0:
            raise TypeError(f"The {runinfo_read_len} value must be non-negative.")

        # Calculate the difference: input_integer - str_length
        str_length = len(index_str)
        n_value = runinfo_index_len - str_length

        # Format the overridecycle string
        overridecycle_string = f"Y{runinfo_read_len};I{str_length}N{n_value};I{str_length}N{n_value};Y{runinfo_read_len},"

        return overridecycle_string

    # def dict_to_illumina_v2_csv(self, header_dict: dict, reads_dict: dict, samples_dict: dict, output_file_name: str):
    #     """
    #     Generate a basic CSV file from provided dictionaries containing header, settings, and sample data.

    #     This method takes three dictionaries (`header_dict`, `reads_dict`, and `samples_dict`), and writes
    #     their contents into a CSV file. The output CSV file is structured with sections for headers, settings,
    #     and sample data, where each dictionary corresponds to a different section in the file.

    #     Args:
    #         header_dict (dict): A dictionary containing header information (e.g., metadata or project info).
    #         reads_dict (dict): A dictionary containing reads data.
    #         samples_dict (dict): A dictionary where each entry corresponds to a sample with its associated data.
    #         output_file_name (str): The base name of the CSV file to be generated (without the ".csv" extension).

    #     Returns:
    #         None: The method writes data to a CSV file and does not return anything.

    #     Raises:
    #         IOError: If there is an error writing to the file.
    #     """
    #     output_file = output_file_name + ".csv"
    #     # Open the output file
    #     with open(output_file, "w", encoding="ASCII") as f:
    #         # Write the Header section
    #         if header_dict:
    #             f.write("[Header]\n")
    #             for key, value in header_dict.items():
    #                 f.write(f"{key},{value}\n")

    #         # Write the Reads section
    #         if reads_dict:
    #             f.write("\n[Reads]\n")
    #             for key, value in reads_dict.items():
    #                 f.write(f"{key},{value}\n")

    #         # Write the Sample section
    #         if samples_dict:
    #             f.write("\n[Data]\n")
    #             # Collect all unique column headers from samples_dict
    #             headers = set()
    #             for sample_info in samples_dict.values():
    #                 headers.update(sample_info.keys())

    #             # Write the column headers to the file
    #             headers = sorted(headers)
    #             f.write(",".join(headers) + "\n")

    #             # Write each sample's data
    #             for sample_id, sample_info in samples_dict.items():  # pylint: disable=unused-variable
    #                 f.write(",".join([str(sample_info.get(h, "")) for h in headers]) + "\n")

    # def convert_to_bcl_compliant(self, input_csv_file, output_file_name: str, bcl_settings_dict: dict, bcl_data_dict: dict):
    #     """
    #     Convert a given samplesheet CSV to a BCL Convert v2-compliant samplesheet,
    #     adding [BCLConvert_Settings] and [BCLConvert_Data] sections at the bottom from provided dictionaries.

    #     Args:
    #         input_csv_file (str): The path to the input CSV file.
    #         output_file_name (str): The base name of the output CSV file to be generated (without the ".csv" extension).
    #         bcl_settings_dict (dict): A dictionary containing BCL settings to be included in the output.
    #         bcl_data_dict (dict): A dictionary containing BCL data to be included in the output.

    #     Returns:
    #         None: The method writes a BCL Convert v2-compliant samplesheet CSV file.
    #     """
    #     output_file = output_file_name + ".csv"

    #     if not os.path.isfile(input_csv_file):
    #         raise FileNotFoundError(f"'{input_csv_file}' does not exist.")

    #     # Open the input CSV and the final output file
    #     with open(input_csv_file, "r", encoding="ASCII") as infile, open(output_file, "w", encoding="ASCII") as outfile:
    #         # Step 1: Copy existing content from the input CSV
    #         for line in infile:
    #             outfile.write(line)

    #         # Add the [BCLConvert_Settings] section at the bottom
    #         if bcl_settings_dict:
    #             outfile.write("\n[BCLConvert_Settings]\n")
    #             for key, value in bcl_settings_dict.items():
    #                 outfile.write(f"{key},{value}\n")

    #         # Add the [BCLConvert_Data] section after the settings at the bottom
    #         if bcl_data_dict:
    #             outfile.write("\n[BCLConvert_Data]\n")
    #             # Collect all unique column headers from samples_dict
    #             headers = set()
    #             for sample_info in bcl_data_dict.values():
    #                 headers.update(sample_info.keys())

    #             # Write the column headers to the file
    #             headers = sorted(headers)
    #             outfile.write(",".join(headers) + "\n")

    #             # Write each sample's data
    #             for sample_id, sample_info in bcl_data_dict.items():  # pylint: disable=unused-variable
    #                 outfile.write(",".join([str(sample_info.get(h, "")) for h in headers]) + "\n")

    # def create_bcl_v2_sample_sheet(
    #     self, output_file_name: str, header_dict: dict, reads_dict: dict, samples_dict: dict, bcl_settings_dict: dict, bcl_data_dict: dict
    # ):
    #     """
    #     Create a BCL Convert v2-compliant sample sheet from provided dictionaries.

    #     Args:
    #         output_file_name (str): The base name of the CSV file to be generated (without the ".csv" extension).
    #         header_dict (dict): A dictionary containing header information (e.g., metadata or project info).
    #         reads_dict (dict): A dictionary containing reads data.
    #         samples_dict (dict): A dictionary where each entry corresponds to a sample with its associated data.
    #         bcl_settings_dict (dict): A dictionary containing BCL settings data.
    #         bcl_data_dict (dict): A dictionary containing BCL data.

    #     Returns:
    #         None: The method writes data to a CSV file.
    #     """

    #     # Step 1: Generate initial CSV using dict_to_illumina_v2_csv
    #     illumina_file_name = output_file_name + "_illumina"  # General Illumina samplesheet
    #     self.dict_to_illumina_v2_csv(header_dict, reads_dict, samples_dict, illumina_file_name)

    #     # Step 2: Convert the temporary CSV to BCL compliant format
    #     bclconvert_file_name = output_file_name + "_bclconvert"
    #     self.convert_to_bcl_compliant(illumina_file_name + ".csv", bclconvert_file_name, bcl_settings_dict, bcl_data_dict)

    def generate_bcl_samplesheet(
        self, header_dict: dict, reads_dict: dict, bcl_settings_dict: dict = None, bcl_data_dict: dict = None, output_file_name: str = "samplesheet"
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
        output_file = output_file_name + ".csv"
        # Open the output file
        with open(output_file, "w", encoding="ASCII") as f:
            # Write the Header section
            if header_dict:
                f.write("[Header]\n")
                for key, value in header_dict.items():
                    f.write(f"{key},{value}\n")

            # Write the Reads section
            if reads_dict:
                f.write("\n[Reads]\n")
                for key, value in reads_dict.items():
                    f.write(f"{key},{value}\n")

            # Add the [BCLConvert_Settings] section at the bottom
            if bcl_settings_dict:
                f.write("\n[BCLConvert_Settings]\n")
                for key, value in bcl_settings_dict.items():
                    f.write(f"{key},{value}\n")

            # Add the [BCLConvert_Data] section after the settings at the bottom
            if bcl_data_dict:
                f.write("\n[BCLConvert_Data]\n")
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

    def generate_bcl_samplesheet_from_runid_xml(self, runid: str, xml_file, output_file_name: str = "samplesheet"):

        # Collect sample info
        cl = ClarityHelperLims()
        sample_info = cl.collect_samplesheet_info(runid)
        bcl_data_dict = cl.reformat_barcode_to_index(sample_info)

        # Extract relevant info from the xml file
        xml_info = self.merge_runinfo_dict_fromfile(xml_file)
        print(xml_info)

        # last step
        # self.generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, bcl_data_dict, output_file_name)

    # def extract_top_unknown_barcode_from_html(self, html_file) -> str:
    #     """
    #     Extract the 'sequence' value with the highest 'count' under "Top Unknown Barcodes" from the HTML file.

    #     Args:
    #         html_file (file-like object): The HTML file containing the "Top Unknown Barcodes" table.

    #     Returns:
    #         str: The top unknown barcode sequence with the highest count.
    #     """
    #     if not os.path.isfile(html_file):
    #         raise FileNotFoundError(f"{html_file} does not exist or is not a file.")

    #     soup = BeautifulSoup(html_file, 'html.parser')

    #     validate_html_format = soup.find('html')
    #     if validate_html_format is None:
    #         raise ValueError("Input file is not HTML.")

    #     # Locate the "Top Unknown Barcodes" table or section
    #     top_barcodes_table = soup.find(text="Top Unknown Barcodes")
    #     if not top_barcodes_table:
    #         raise ValueError("Could not find 'Top Unknown Barcodes' in the HTML file")

    #     # Find the associated table or section containing the sequence and count
    #     table = top_barcodes_table.find_next("table")
    #     if not table:
    #         raise ValueError("Could not find a table after 'Top Unknown Barcodes'")

    #     # Parse the table for rows of barcode sequences and counts
    #     rows = table.find_all("tr")
    #     max_count = 0
    #     top_sequence = None
    #     for row in rows[1:]:  # Skip header row
    #         columns = row.find_all("td")
    #         sequence = columns[0].text.strip()
    #         count = int(columns[1].text.strip())
    #         if count > max_count:
    #             max_count = count
    #             top_sequence = sequence

    #     if not top_sequence:
    #         raise ValueError("Could not find a valid sequence in the table")

    #     return top_sequence

    # def process_sample_sheet(self, mode: IndexMode, html_file=None, input_samplesheet=None, output_samplesheet_name: str = None,
    #                         header_dict=None, reads_dict=None, samples_dict=None, bcl_settings_dict=None, bcl_data_dict=None):
    #     """
    #     Process the input sample sheet based on the mode (either IndexMode.SINGLE_INDEX or IndexMode.DUAL_INDEX).

    #     Args:
    #         mode (IndexMode): Either IndexMode.SINGLE_INDEX or IndexMode.DUAL_INDEX.
    #         html_file (file-like object, optional): The HTML file to scan for the top unknown barcode (only used in dual_index mode).
    #         input_samplesheet (file-like object, optional): The CSV file representing the input sample sheet (only for dual_index mode).
    #         output_samplesheet_name (str, optional): The output CSV file name to be generated. For dual_index mode, if not provided,
    #                                                 it will append '_dual_index.csv' to the input filename.
    #         header_dict (dict, optional): Required in SINGLE_INDEX mode. A dictionary containing header information for the BCL v2 sample sheet.
    #         reads_dict (dict, optional): Required in SINGLE_INDEX mode. A dictionary containing reads information for the BCL v2 sample sheet.
    #         samples_dict (dict, optional): Required in SINGLE_INDEX mode. A dictionary containing sample data for the BCL v2 sample sheet.
    #         bcl_settings_dict (dict, optional): Required in SINGLE_INDEX mode. A dictionary containing settings for the BCL v2 sample sheet.
    #         bcl_data_dict (dict, optional): Required in SINGLE_INDEX mode. A dictionary containing BCL data for the BCL v2 sample sheet.

    #     Returns:
    #         None: Writes to the output sample sheet CSV file.
    #     """
    #     # Mode: SINGLE_INDEX
    #     if mode == IndexMode.SINGLE_INDEX:
    #         if not header_dict or not reads_dict or not samples_dict or not bcl_settings_dict or not bcl_data_dict:
    #             raise ValueError("All required dictionaries must be provided for single index mode")

    #         # Use create_bcl_v2_sample_sheet to create the BCL v2 sample sheet
    #         if output_samplesheet_name is None:
    #             output_samplesheet_name = "illumina_samplesheet_single_index.csv"  # Default output name

    #         # Call the method to create the sample sheet
    #         self.create_bcl_v2_sample_sheet(header_dict, reads_dict, samples_dict, bcl_settings_dict, bcl_data_dict, output_samplesheet_name)

    #     # Mode: DUAL_INDEX
    #     elif mode == IndexMode.DUAL_INDEX:
    #         # Check thee input required are present and in file format
    #         if not html_file or not input_samplesheet:
    #             raise ValueError("An input sample sheet and HTML file must be provided in dual index mode.")

    #         if not os.path.isfile(input_samplesheet):
    #             raise FileNotFoundError(f"{input_samplesheet} does not exist or is not a file.")

    #         # Extract top barcode from the HTML file
    #         top_sequence = self.extract_top_unknown_barcode_from_html(html_file)

    #         # Set default output file name if not provided
    #         if output_samplesheet_name is None:
    #             # Use the input file name and append "_dual_index.csv"
    #             input_filename = os.path.basename(input_samplesheet.name)
    #             file_root, file_ext = os.path.splitext(input_filename)
    #             output_samplesheet_name = f"{file_root}_dual_index.csv"

    #         # Read and modify the sample sheet
    #         updated_rows = []
    #         reader = csv.DictReader(input_samplesheet)
    #         fieldnames = reader.fieldnames

    #         if "index2" not in fieldnames:
    #             fieldnames.append("index2")  # Add the 'index2' column if not present

    #         for row in reader:
    #             row['index2'] = top_sequence  # Assign top barcode sequence to 'index2'
    #             updated_rows.append(row)

    #         # Write the updated sample sheet to a new file
    #         with open(output_samplesheet_name, "w", newline="") as output_csv:
    #             writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    #             writer.writeheader()
    #             writer.writerows(updated_rows)

    #     else:
    #         raise ValueError("Mode must be either Mode.SINGLE_INDEX or Mode.DUAL_INDEX.")
