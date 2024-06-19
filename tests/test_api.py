"""
Clarity API Tests
"""

# pylint: disable=missing-function-docstring

import unittest
import pytest
# from tests.mocks.mock_clarity_lims import MockClarityLims
from asf_tools.api.clarity.clarity_lims import ClarityLims

# MOCK_API_DATA_DIR = "tests/data/api/clarity/mock_data"


class TestClarity(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        self.api = ClarityLims()

    def test_get_artifacts_from_runid_isnone(self):
        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_artifacts_from_runid(None)

    def test_get_artifacts_from_runid_isinvalid(self):
        # Setup
        runid = 'fake_runid'

        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_artifacts_from_runid(runid)

    def test_get_samples_from_artifacts_isnone(self):
        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_samples_from_artifacts(None)

    def test_get_samples_from_artifacts_isinvalid(self):
        # Setup
        artifacts_list = ['fake_list']

        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_samples_from_artifacts(artifacts_list)

        # Setup
        # do we want to test for en empty list? (ie. list = [])
        # Test and Assert
        # self.api.get_samples_from_artifacts()

    # test get_sample_info function
    def test_get_sample_info_isnone(self):
        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_info(None)

    def test_get_sample_info_isinvalid(self):
        # Setup
        sample = 'fake_sample'
        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_sample_info(sample)


class TestClarityWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self):
        """Setup API connection"""
        yield ClarityLims()

    @pytest.mark.parametrize("runid,expected", [
        ("20240417_1729_1C_PAW45723_05bb74c5", 1)
    ])
    def test_get_artifacts_from_runid_valid(self, api, runid, expected):  # pylint: disable=missing-function-docstring
        # Test
        artifacts = api.get_artifacts_from_runid(runid)

        # Assert
        assert len(artifacts) == expected


# class TestClarityMocks:
#     """
#     Mock generation methods
#     """
#     @pytest.mark.only_run_with_direct_target
#     def test_mocking_generate_clarity_data(self):
#         """
#         Generates a new test data set from the api
#         """

#         MockClarityLims.generate_test_data(MOCK_API_DATA_DIR)

class TestClarityPrototype(unittest.TestCase):
    def setUp(self):
        self.api = ClarityLims()

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
        print(run_placement)

        sample_list = []
        for value in run_placement:
            run_samples = value.samples
            sample_list.extend(run_samples)
        print(sample_list)

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
        lims = ClarityLims()

        run_id = "20240417_1729_1C_PAW45723_05bb74c5"
        run_container = lims.get_containers(name=run_id)[0]
        artifacts = lims.get_artifacts(containername=run_container.name)

        for artifact in artifacts:
            initial_process = artifact.parent_process
            sample_barcode_match = {}

            if initial_process is None:
                raise ValueError("Initial process is None")
            visited_processes = set()
            stack = [initial_process]
            print(stack)

            while stack:
                process = stack.pop()
                if process.id in visited_processes:
                    continue

                visited_processes.add(process.id)

                if process.type.name != "T Custom Indexing":
                    # print(process.type.name)
                    # Add parent processes to the stack for further processing
                    for input, output in process.input_output_maps:
                        if output["output-type"] == "Analyte":
                            parent_process = input.get('parent-process')
                            if parent_process:
                                stack.append(parent_process)
                else:
                    # Extract barcode information and store it in "sample_barcode_match"
                    for input, output in process.input_output_maps:
                        if output["output-type"] == "Analyte":
                            uri = output['uri']
                            sample_info = uri.samples[0]
                            sample_name = sample_info.id
                            reagent_barcode = uri.reagent_labels
                            sample_barcode_match[sample_name] = {"barcode": reagent_barcode}
                    print(sample_barcode_match)
                    
                    # return sample_barcode_match
        raise ValueError