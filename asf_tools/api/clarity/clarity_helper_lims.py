"""
Clarity API Child class with helper functions
"""

import logging
from typing import Optional

from asf_tools.api.clarity.clarity_lims import ClarityLims
from asf_tools.api.clarity.models import Artifact, ResearcherStub, Lab, Process

log = logging.getLogger(__name__)

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
        values = self.expand_stubs(artifacts_list, expansion_type = Artifact)
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
        name, associated project, user, and lab group. If the sample is None, an appropriate
        exception is raised.

        Args:
            sample (str): The unique identifier for the sample whose information is to be retrieved.

        Returns:
            dict: A dictionary containing detailed information about the sample, including:
                - sample_name (str): The name of the sample.
                - group (str): The lab group associated with the sample.
                - user (str): The user associated with the sample.
                - project_id (str): The project ID associated with the sample.

        Raises:
            ValueError: If the provided sample is None.

        """
        if sample is None:
            raise ValueError("sample is None")

        # Retrieve the expanded sample stub and extract name, project ID, lab and researcher name
        sample_stub = self.get_samples(search_id = sample)
        # print(sample_stub)
        sample_name = sample_stub.name
        project_id = self.get_projects(search_id = sample_stub.project.id)
        project_id = project_id.name

        # user = self.expand_stub(sample, expansion_type = ResearcherStub)
        # user_name = user.submitter.first_name 
        # user_lastname = user.submitter.last_name
        # user_fullname = (user_name + '.' + user_lastname).lower()
        user_fullname = "placeholder.name"

        # lab = user.submitter.lab.name #shouldn't work
        lab = "placeholder_lab"

        # Store obtained information in a dictionary
        sample_info = {}
        sample_info[sample_name] = {
            "group": lab, 
            "user": user_fullname, 
            "project_id": project_id
            }
        # print(sample_info)

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

    def get_sample_barcode(self, run_id: str) -> dict:
        if run_id is None:
            raise ValueError("run_id is None")

        artifacts_list = self.get_artifacts_from_runid(run_id)

        # Extract parent_process information from each artifact
        artifacts_list = self.expand_stubs(artifacts_list, expansion_type = Artifact)  
        initial_parent_process_list = []
        initial_parent_process_list.extend(artifact.parent_process for artifact in artifacts_list)
        initial_process = self.expand_stubs(initial_parent_process_list, expansion_type = Process)

        if initial_process is None:
            raise ValueError("Initial process is None")
        visited_processes = set()
        # print(initial_process)

        sample_barcode_match = {}
        while initial_process:
            process = initial_process.pop()
            # print(process)
            if process.id in visited_processes:
                continue

            visited_processes.add(process.id)

            if process.process_type.name != "T Custom Indexing":
                print(process)
                # Add parent processes to the stack for further processing
                for input_output in process.input_output_map:
                    if input_output.output.output_type == "Analyte":
                        parent_process = input_output.input.parent_process
                        if parent_process:
                            initial_process.append(parent_process)
            # else:
            #     # Extract barcode information and store it in "sample_barcode_match"
            #     for input_output in process.input_output_map:
            #         if input_output.output.output_type == "Analyte":
            #             uri = input_output.output.uri
            #             sample_info = uri.samples[0]
            #             sample_name = sample_info.id
            #             reagent_barcode = uri.reagent_labels
            #             sample_barcode_match[sample_name] = {"barcode": reagent_barcode}
            #     print(sample_barcode_match)

        return sample_barcode_match