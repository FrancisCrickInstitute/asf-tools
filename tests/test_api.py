"""
Clarity API Tests
"""

import unittest
import pytest
from tests.mocks.mock_clarity_lims import MockClarityLims

from asf_tools.api.clarity.clarity_lims import ClarityLims

MOCK_API_DATA_DIR = "tests/data/api/clarity/mock_data"


class TestClarity(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        self.api = MockClarityLims(MOCK_API_DATA_DIR)

    @pytest.mark.only_run_with_direct_target
    def test_mock_clarity_generate_data(self):
        """
        Generates a new test data set from the api
        """

        MockClarityLims.generate_test_data(MOCK_API_DATA_DIR)

    @pytest.mark.only_run_with_direct_target
    def test_clarity_api(self):
        """
        Fetches sample information from Clarity for a given run ID and constructs a dictionary
        with sample names as keys and their respective lab, user, and project ID as values.

        Returns:
            dict: A dictionary containing sample information with the following structure:
                {
                    "sample_name": {
                        "group": "lab_name",
                        "user": "user_fullname",
                        "project_id": "project_id"
                    },
                    ...
                }
        Raises:
            ValueError: If no sample information is found.
        """
        lims = ClarityLims()

        run_id = "20240417_1729_1C_PAW45723_05bb74c5"
        run_container = lims.get_containers(name=run_id)[0]
        # print("Container")
        # print(f"Name: {run_container.name}")
        # print(f"Type: {run_container.type}")
        # print(f"Wells: {run_container.occupied_wells}")
        # print(f"Placements: {run_container.placements}")
        # print(f"UDF: {run_container.udf}")
        # print(f"UDT: {run_container.udt}")
        # print(f"State: {run_container.state}")
        
        # projects = lims.get_projects(name="RN24071")
        # print(projects)

        # get info required to build the samplesheet
        run_placement = run_container.placements
        run_placement = list(run_placement.values())
        # print(run_placement)

        sample_list = []
        for value in run_placement:
            run_samples = value.samples
            sample_list.extend(run_samples)
        # print(sample_list)

        sample_info = {}
        for sample in sample_list:
            sample_name = sample.name
            lab = sample.submitter.lab.name
            user_name = sample.submitter.first_name
            user_lastname = sample.submitter.last_name
            user_fullname = (user_name + '.' + user_lastname).lower()
            project_id = sample.project.name
            # print(lab)
            # print(user_fullname)
            # print(project_id)

            sample_info[sample_name] = {
                "group": lab, 
                "user": user_fullname, 
                "project_id": project_id
                }
        # print(sample_info)
        if not sample_info:
            raise ValueError("No sample information found")

        return sample_info
    
    @pytest.mark.only_run_with_direct_target
    def test_sample_barcode(self):
        # Recursive function that loops through parent_processes
        def parent_process_loop(process, visited_processes=None):
            if visited_processes is None:
                visited_processes = set()
            if process is None:
                raise ValueError
            # check if we have already visited this process to prevent infinite loops
            if process.id in visited_processes:
                return
            visited_processes.add(process.id)

            # stop recursion if the process type is "T Custom Indexing" and extract barcode+sample info
            if process.type.name == "T Custom Indexing":
                sample_barcode_match = {}
                for input, output in process.input_output_maps:
                    if output["output-type"] == "Analyte":
                        uri = output['uri']
                        sample_info = uri.samples[0]
                        sample_name = sample_info.id
                        reagent_barcode = uri.reagent_labels

                sample_barcode_match[sample_name] = { "barcode": reagent_barcode }
                print(sample_barcode_match)
                return sample_barcode_match

            # Recursive case: if not "T Custom Indexing", continue to the parent process
            for input, output in process.input_output_maps:
                if output["output-type"] == "Analyte":
                    parent_process = input['parent-process']
                    if parent_process:
                        parent_process_loop(parent_process, visited_processes)

        lims = ClarityLims()

        run_id = "20240417_1729_1C_PAW45723_05bb74c5"
        run_container = lims.get_containers(name=run_id)[0]
        artifacts = lims.get_artifacts(containername=run_container.name)
        print(run_container)
        print(artifacts)
        for artifact in artifacts:
            initial_process = artifact.parent_process
            if initial_process:
                parent_process_loop(initial_process)

        raise ValueError
    
    @pytest.mark.only_run_with_direct_target
    def test_ONT_samplesheet(self):
        general_info = test_clarity_api()
        barcode_info = test_sample_barcode()
        print(general_info)
        print(barcode_info)