"""
Clarity API Child class with helper functions
"""

import queue
import re
import warnings

from asf_tools.api.clarity.clarity_lims import ClarityLims
from asf_tools.api.clarity.models import Artifact, Lab, Process, Researcher, Sample


class ClarityHelperLims(ClarityLims):
    """
    A helper class extending ClarityLims to provide additional methods for handling
    samples and artifacts in the Clarity LIMS system.

    Methods:
        get_artifacts_from_runid(run_id: str) -> list:
            Retrieve a list of artifacts associated with a given run ID.

        get_samples_from_artifacts(artifacts_list: list) -> list:
            Retrieve a list of unique samples from a given list of artifacts.

        get_sample_info(sample: str) -> dict:
            Retrieve detailed information for a given sample.

        collect_sample_info_from_runid(run_id: str) -> dict:
            Collect detailed information for all samples associated with a given run ID.
    """

    def get_artifacts_from_runid(self, run_id: str) -> list:
        """
        Retrieve a list of artifacts associated with a given run ID.

        This method checks if the specified run ID exists within the Clarity system
        and retrieves the associated artifacts. If the run ID does not exist or is
        None, an appropriate exception is raised.

        Args:
            run_id (str): The unique identifier for the run whose artifacts are to be retrieved.

        Returns:
            list: A list of artifact stubs associated with the specified run ID.

        Raises:
            ValueError: If the provided run_id is None.
            KeyError: If the specified run_id does not exist in the Clarity system.
        """
        if run_id is None:
            raise ValueError("run_id is None")

        # Check that the run ID exists in clarity
        run_containers = self.get_containers(name=run_id)
        if run_containers is None:
            raise KeyError("run_id does not exist")

        # Get a list of artifacts stubs
        run_artifacts = run_containers.placements
        return run_artifacts

    def get_samples_from_artifacts(self, artifacts_list: list) -> list:
        """
        Retrieve a list of unique samples from a given list of artifacts.

        This method expands the provided list of artifact stubs, extracts the associated
        samples, and ensures that the list of samples returned is unique.

        Args:
            artifacts_list (list): A list of artifact stubs from which samples are to be retrieved.

        Returns:
            list: A list of unique samples associated with the provided artifacts.

        Raises:
            ValueError: If the provided artifacts_list is None.

        """
        if artifacts_list is None:
            raise ValueError("artifacts_list is None")

        # Expand each artifact to extract sample information and save it in a list
        sample_list = []
        values = self.expand_stubs(artifacts_list, expansion_type=Artifact)
        for value_item in values:
            run_samples = value_item.samples
            sample_list.extend(run_samples)

        # Make the entries in sample_list unique
        unique_sample_list = list({obj.limsid: obj for obj in sample_list}.values())
        return unique_sample_list

    def get_sample_info(self, sample: str) -> dict:
        """
        Retrieve detailed information for a given sample.

        This method fetches information related to a specified sample, including its
        name, associated project, user, lab group, project type, reference genome used and data analysis type. If the sample is None, an appropriate
        exception is raised.

        Args:
            sample (str): The unique identifier for the sample whose information is to be retrieved.

        Returns:
            dict: A dictionary containing detailed information about the sample, including:
                - sample_name (str): The name of the sample.
                - group (str): The lab group associated with the sample.
                - user (str): The user associated with the sample.
                - project_id (str): The project ID associated with the sample.
                - project_type (str or None): The project type associated with the sample.
                - reference_genome (str or None): The reference genome associated with the sample.
                - data_analysis_type (str or None): The data analysis pipeline associated with the sample.


        Raises:
            ValueError: If the provided sample is None.

        """
        if sample is None:
            raise ValueError("sample is None")

        # Expand sample stub and get name which is the ASF sample id
        sample = self.get_samples(search_id=sample)
        sample_id = sample.id
        sample_name = sample.name

        # Extract project wide info
        sample_project = sample.project
        if sample_project:
            project = self.get_projects(search_id=sample.project.id)
            project_name = project.name
            project_limsid = project.id
            project_type = next((item.value for item in project.udf_fields if item.name == "Project Type"), None)
            reference_genome = next((item.value for item in project.udf_fields if item.name == "Reference Genome"), None)
            data_analysis_type = next((item.value for item in project.udf_fields if item.name == "Data Analysis Pipeline"), None)
        else:
            project_name = None
            project_limsid = None
            project_type = None
            reference_genome = None
            data_analysis_type = None

        # Get the submitter details
        if sample_project:
            user = self.get_researchers(search_id=project.researcher.id)
        else:
            user = self.get_researchers(search_id=sample.submitter.id)

        # these get the submitter, not the scientist, info
        user_firstname = user.first_name
        user_lastname = user.last_name
        user_fullname = (user_firstname + "." + user_lastname).lower()

        # Get the lab details
        lab = self.expand_stub(user.lab, expansion_type=Lab)
        lab_name = lab.name

        # Store obtained information in a dictionary
        sample_info = {}
        sample_info[sample_id] = {
            "sample_name": sample_name,
            "group": lab_name,
            "user": user_fullname,
            "project_id": project_name,
            "project_limsid": project_limsid,
            "project_type": project_type,
            "reference_genome": reference_genome,
            "data_analysis_type": data_analysis_type,
        }

        return sample_info

    def collect_sample_info_from_runid(self, run_id: str) -> dict:
        """
        Collect detailed information for all samples associated with a given run ID.

        This method retrieves all artifacts associated with the specified run ID, extracts
        the unique samples from these artifacts, and then collects detailed information for
        each sample. The collected information is returned as a dictionary.

        Args:
            run_id (str): The unique identifier for the run whose sample information is to be collected.

        Returns:
            dict: A dictionary containing detailed information for all samples associated with the run ID.
                The structure of the dictionary is as follows:
                {
                    sample_name (str): {
                        "group": lab (str),
                        "user": user_fullname (str),
                        "project_id": project_id (str)
                    },
                    ...
                }

        Raises:
            ValueError: If the provided run_id is None or invalid.
            KeyError: If the run_id does not exist in the system.
        """
        # Obtain an artifacts list and then use it as input to obtain a sample list
        artifacts_list = self.get_artifacts_from_runid(run_id)
        sample_list = self.get_samples_from_artifacts(artifacts_list)

        # Store detailed information from all samples in sample_list within a dictionary
        sample_info = {}
        for sample_id in sample_list:
            info = self.get_sample_info(sample_id.id)
            sample_info.update(info)
        return sample_info

    def get_sample_barcode_from_runid(self, run_id: str) -> dict:
        """
        Retrieve a mapping of sample barcodes for all samples associated with a given run ID.

        This method retrieves all artifacts associated with the specified run ID, traverses
        the parent processes to find the "T Custom Indexing" process, and collects barcode
        information for each sample. The collected information is returned as a dictionary.

        Args:
            run_id (str): The unique identifier for the run whose sample barcodes are to be retrieved.

        Returns:
            dict: A dictionary containing the mapping of sample names to their barcodes.
                The structure of the dictionary is as follows:
                {
                    sample_name (str): {
                        "barcode": reagent_barcode (str)
                    },
                    ...
                }

        Raises:
            ValueError: If the provided run_id is None or invalid.
            ValueError: If the initial process is None.
        """
        artifacts_list = self.get_artifacts_from_runid(run_id)

        # Extract parent_process information from each artifact
        artifacts_list = self.expand_stubs(artifacts_list, expansion_type=Artifact)
        initial_parent_process_list = []
        initial_parent_process_list.extend(artifact.parent_process for artifact in artifacts_list if artifact.parent_process is not None)
        initial_process = self.expand_stubs(initial_parent_process_list, expansion_type=Process)

        if initial_process is None:
            raise ValueError("Initial process is None")

        # Set up for a binary search tree
        visited_processes = set()
        process_queue = queue.Queue()
        for item in initial_process:
            process_queue.put(item)

        sample_barcode_match = {}
        # Loop through parent process until the "T Custom Indexing"
        while process_queue.qsize() > 0:
            process = process_queue.get()
            if process.id in visited_processes:
                continue

            visited_processes.add(process.id)

            if process.process_type.name != "T Custom Indexing":
                # Add parent processes to the stack for further processing
                for input_output in process.input_output_map:
                    if input_output.output.output_type == "Analyte":
                        parent_process = input_output.input.parent_process
                        if parent_process:
                            parent_process = self.expand_stub(parent_process, expansion_type=Process)
                            process_queue.put(parent_process)
            else:
                # Extract barcode information and store it in "sample_barcode_match"
                for input_output in process.input_output_map:
                    if input_output.output.output_type == "Analyte":
                        output_expanded = self.expand_stub(input_output.output, expansion_type=Artifact)
                        sample_stub = output_expanded.samples[0]
                        sample_info = self.expand_stub(sample_stub, expansion_type=Sample)
                        sample_name = sample_info.id
                        reagent_barcode = output_expanded.reagent_labels[0]
                        sample_barcode_match[sample_name] = {"barcode": reagent_barcode}

        return sample_barcode_match

    def get_sample_custom_barcode_from_runid(self, run_id: str) -> dict:
        """
        Retrieve a mapping of custom barcodes for all samples associated with a given run ID.

        This method first retrieves all artifacts associated with the specified run ID, then extracts
        the list of samples from these artifacts. For each sample, it fetches detailed information and
        extracts the custom barcode from a UDF field named "Index". The resulting mapping of sample names
        to their barcodes is returned.

        Args:
            run_id (str): The unique identifier for the run whose sample barcodes are to be retrieved.

        Returns:
            dict: A dictionary where each key is the sample name (str), and the value is a dictionary containing:
                - "barcode": The custom barcode (str) associated with the sample.

        Raises:
            ValueError: If the provided run_id is None or invalid.
            KeyError: If the run_id does not exist in the system.
        """

        # Obtain an artifacts list and then use it as input to obtain a sample list
        artifacts_list = self.get_artifacts_from_runid(run_id)
        sample_list = self.get_samples_from_artifacts(artifacts_list)

        # Extract barcodes
        sample_barcode = {}
        for sample_id in sample_list:
            info = self.get_samples(search_id=sample_id.id)
            sample_name = info.id
            reagent_barcode = next((entry.value for entry in info.udf_fields if entry.name == "Index"), "")
            sample_barcode[sample_name] = {"barcode": reagent_barcode}

        return sample_barcode

    def reformat_barcode_to_index(self, barcode_dict: dict) -> dict:
        """
        Extract a mapping of indices from sample barcodes.

        This function processes a dictionary of samples and extracts the index
        values from the barcode information located within parentheses. For each
        sample, it retrieves the barcode and determines the index and index2 values
        based on a regex pattern: letters followed by any character, then more letters.
        If no match is found, 'index' will be set to the entire section inside the
        parentheses, and 'index2' will be an empty string. If no valid barcodes are found,
        a warning is logged.

        Args:
            sample_info (dict): A dictionary where each key is a sample ID
                (str), and the value is another dictionary containing sample metadata,
                including a 'barcode' key.

        Returns:
            dict: A dictionary where each key is a sample ID (str), and the value
                is another dictionary containing:
                    - "index": The extracted index value (str) from the barcode.
                    - "index2": The extracted index2 value (str), or an empty string
                    if no dash was found.

        Raises:
            UserWarning: If no valid barcode values are found in the provided samples.
        """
        extracted_info = {}
        has_valid_barcodes = False  # Track whether we find any valid barcodes

        # Define the regex pattern
        pattern = r"([a-zA-Z]+)([^\w\s]+)([a-zA-Z]+)"

        for sample_id, sample_data in barcode_dict.items():
            # Get the barcode string
            barcode = sample_data.get("barcode", "")

            if barcode is None:
                # Treat None as a blank string
                barcode = ""

            # Extract the sequence inside the parentheses
            if "(" in barcode and ")" in barcode:
                barcode_section = barcode.split("(")[-1].split(")")[0]

                # Search for the regex pattern
                match = re.search(pattern, barcode_section)

                # Check if a match was found (ie. Split the section at the dash "-")
                if match:
                    index, separator, index2 = match.groups()
                else:
                    # If no match, assign the whole section to index and keep index2 empty
                    index, index2 = barcode_section, ""

                # Assign the extracted values to a new dictionary
                extracted_info[sample_id] = {"index": index, "index2": index2}

                has_valid_barcodes = True  # Mark that we found a valid barcode

        # Check if no barcodes were processed and raise a warning
        if not has_valid_barcodes:
            warnings.warn("No valid barcode values found in the provided samples.", UserWarning)

        return extracted_info

    def collect_samplesheet_info(self, run_id: str) -> dict:
        """
        Collect and merge detailed information for all samples associated with a given run ID for ONT samplesheet.

        This method retrieves sample metadata and barcode information for all samples associated
        with the specified run ID, and merges this information into a single dictionary. The merged
        information is useful for generating an ONT samplesheet.

        Args:
            run_id (str): The unique identifier for the run whose samplesheet information is to be collected.

        Returns:
            dict: A dictionary containing merged information for all samples associated with the run ID.
                The structure of the dictionary is as follows:
                {
                    sample_name (str): {
                        "group": lab (str),
                        "user": user_fullname (str),
                        "project_id": project_id (str),
                        "project_type": project_type (str or None),
                        "reference_genome": reference_genome (str or None),
                        "data_analysis_type": data_analysis_type (str or None),
                        "barcode": reagent_barcode (str)
                    },
                    ...
                }

        Raises:
            ValueError: If the provided run_id is None or invalid.
        """
        # Collect sample info
        sample_metadata = self.collect_sample_info_from_runid(run_id)
        barcode_info = self.get_sample_barcode_from_runid(run_id)
        # Check if barcode_info is empty; if so, use get_sample_custom_barcode to fetch it
        if not barcode_info:
            barcode_info = self.get_sample_custom_barcode_from_runid(run_id)

        # Merge dictionaries using sample names as keys
        merged_dict = sample_metadata
        for key, value in barcode_info.items():
            for sub_key, sub_value in value.items():
                if key in merged_dict:
                    merged_dict[key][sub_key] = sub_value

        return merged_dict


# currently index,index2 and Index_ID is all merged into "barcode"
# this is the header created by the perl scripts:
# Lane,Sample_ID,User_Sample_Name,index,index2,Index_ID,Sample_Project,Project_limsid,User,Lab,ReferenceGenome,DataAnalysisType
# 1,TLG66A2880,U_LTX1369_BS_GL,CTAAGGTC,,SXT 51 C07 (CTAAGGTC),TRACERx_Lung,TLG66,tracerx.tlg,swantonc,Homo sapiens,Whole Exome
# 1,TLG66A2881,U_LTX1369_SU_T1-R1,CGACACAC,,SXT 52 D07 (CGACACAC),TRACERx_Lung,TLG66,tracerx.tlg,swantonc,Homo sapiens,Whole Exome
